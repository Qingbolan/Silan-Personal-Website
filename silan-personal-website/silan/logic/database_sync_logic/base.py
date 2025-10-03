"""Core orchestration helpers for database synchronization."""

import hashlib
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from rich.progress import TaskID
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import Session, sessionmaker

from ...core.exceptions import DatabaseError, ValidationError
from ...models import (
    Base,
    User,
    BlogPost,
    BlogPostTag,
    BlogPostTranslation,
    Project,
    ProjectTechnology,
    ProjectDetail,
    Idea,
    RecentUpdate,
)
from ...utils import CLIInterface, ConfigManager, FileOperations
from ..content_logic import ContentLogic
from ...utils import ModernLogger


class DatabaseSyncBase(ModernLogger):
    """Shared workflow, configuration, and utility helpers for sync."""

    def __init__(self, database_config: Union[str, Dict[str, Any]], dry_run: bool = False):
        super().__init__(name="db_sync", level="info")
        self.database_config = database_config
        self.dry_run = dry_run
        self.cli = CLIInterface(self)
        self.file_ops = FileOperations(self)

        # Initialize sub-components
        self.content_logic = ContentLogic()
        self.config_manager = ConfigManager(Path.cwd())

        # Database components
        self.engine = None
        self.session_factory = None
        self.current_user_id = None

        # Sync statistics
        self.sync_stats = {
            'total_items': 0,
            'processed_items': 0,
            'success_count': 0,
            'error_count': 0,
            'skipped_count': 0,
            'created_count': 0,
            'updated_count': 0,
            'deleted_count': 0,
            'sync_errors': [],
            'sync_warnings': []
        }

    def sync_start(self, db_type: str, content_count: int) -> None:
        """Log sync operation start."""
        self.stage(f"Starting sync to {db_type} database")
        self.info(f"📚 Found {content_count} content items to process")

    def sync_progress(self, current: int, total: int, item_name: str) -> None:
        """Log sync progress."""
        self.debug(f"Syncing ({current}/{total}): {item_name}")

    def sync_complete(self, success_count: int, error_count: int) -> None:
        """Log sync completion."""
        if error_count == 0:
            self.success(f"✅ Sync completed: {success_count} items processed successfully")
        else:
            self.warning(
                f"⚠️ Sync completed with {error_count} errors: {success_count} success, {error_count} failed"
            )

    def validate_configuration(self) -> bool:
        """Validate database configuration"""
        if isinstance(self.database_config, dict):
            self._validate_database_dict(self.database_config)
        elif isinstance(self.database_config, str):
            if not self.database_config.strip():
                raise ValidationError("Database connection string cannot be empty")
        else:
            raise ValidationError("Database config must be dict or string")

        return True


    def _validate_database_dict(self, config: Dict[str, Any]) -> None:
        """Validate database configuration dictionary"""
        if 'type' not in config:
            raise ValidationError("Database config missing 'type' field")

        db_type = config['type']
        if db_type not in ['mysql', 'postgresql', 'sqlite']:
            raise ValidationError(f"Unsupported database type: {db_type}")

        if db_type in ['mysql', 'postgresql']:
            required_keys = ['host', 'user', 'database']
            for key in required_keys:
                if key not in config:
                    raise ValidationError(f"Missing required database config: {key}")

        elif db_type == 'sqlite':
            if 'path' not in config:
                # Auto-create default SQLite path instead of throwing error
                config['path'] = 'portfolio.db'
                self.info(f"No SQLite path specified, using default: {config['path']}")

    def show_sync_overview(self) -> None:
        """Display synchronization overview"""
        self.section("Database Synchronization Overview")

        # Database configuration info
        db_info = self._get_database_info()
        self.cli.display_info_panel("Database Configuration", db_info)

        # Content analysis
        content_analysis = self.content_logic.analyze_content_for_sync()
        self.cli.display_info_panel("Content Analysis", content_analysis)

        if self.dry_run:
            self.info("🧪 Running in DRY RUN mode - no changes will be made")

    def _get_database_info(self) -> Dict[str, Any]:
        """Get database configuration info for display"""
        if isinstance(self.database_config, str):
            return {'Type': 'Custom connection string', 'Connection': self.database_config[:50] + '...'}

        config = self.database_config
        info = {'Type': config['type'].upper()}

        if config['type'] == 'sqlite':
            info['Database File'] = config['path']
        else:
            info['Host'] = f"{config['host']}:{config.get('port', 'default')}"
            info['Database'] = config['database']
            info['User'] = config['user']

        return info

    def execute_sync(self, create_tables: bool = False) -> bool:
        """Execute the database synchronization"""
        try:
            # Initialize database connection
            if not self._initialize_database():
                return False

            # Always check if basic tables exist, create if needed
            try:
                if self.session_factory:
                    with self.session_factory() as session:
                        # Test if basic tables exist by trying to query users table
                        session.execute(text("SELECT COUNT(*) FROM users LIMIT 1"))
                else:
                    raise DatabaseError("Session factory not initialized")
            except Exception as e:
                # If query fails, tables likely don't exist
                self.warning(f"Database tables not found or incomplete: {e}")
                self.info("🔧 Automatically creating database tables...")
                create_tables = True

            # Create tables if requested or if they don't exist
            if create_tables:
                self._create_database_tables()

            # Get content to sync
            content_items = self.content_logic.get_all_content_for_sync()
            self.sync_stats['total_items'] = len(content_items)

            if not content_items:
                self.info("📋 No content found to sync")
                return True

            # Start sync process
            self.sync_start(
                self._get_database_type(),
                len(content_items)
            )

            # Process content items
            progress, raw_task_id = self.progress(len(content_items), "Syncing content")
            task_id = cast(TaskID, raw_task_id)
            progress.start()
            try:
                for i, item in enumerate(content_items):
                    try:
                        if self.dry_run:
                            self._simulate_sync_item(item)
                        else:
                            self._sync_content_item(item)

                        self.sync_stats['success_count'] += 1
                        self.sync_progress(i + 1, len(content_items), item['name'])

                    except Exception as e:
                        error_msg = f"Failed to sync {item['path']}: {e}"
                        self.error(error_msg)
                        self.sync_stats['error_count'] += 1
                        self.sync_stats['sync_errors'].append(error_msg)

                    self.sync_stats['processed_items'] += 1
                    progress.update(task_id, advance=1)
            finally:
                progress.stop()

            # Handle deleted files - clean up orphaned database records
            if self.dry_run:
                self._simulate_cleanup_deleted_content(content_items)
            else:
                self._cleanup_deleted_content(content_items)

            # Log completion
            self.sync_complete(
                self.sync_stats['success_count'],
                self.sync_stats['error_count']
            )

            # Save sync summary
            if not self.dry_run:
                self.save_sync_summary()
                # Update config files with sync metadata
                self._update_config_sync_metadata()

            # Display final statistics
            self._display_sync_results()

            return self.sync_stats['error_count'] == 0

        except Exception as e:
            self.error(f"Sync execution failed: {e}")
            return False
        finally:
            self._cleanup_database()

    def _initialize_database(self) -> bool:
        """Initialize database connection"""
        try:
            connection_string = self._build_connection_string()
            self.debug(f"Connection string: {connection_string}")
            self.engine = create_engine(
                connection_string,
                echo=False,
                pool_pre_ping=True
            )

            # Test connection
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)

            return True
        except Exception as e:
            self.error(f"Database initialization failed: {e}")
            return False

    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string"""
        if isinstance(self.database_config, str):
            return self.database_config

        config = self.database_config
        db_type = config['type']

        if db_type == 'sqlite':
            db_path = config['path']
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"

        elif db_type == 'mysql':
            host = config['host']
            port = config.get('port', 3306)
            user = config['user']
            password = config.get('password', '')
            database = config['database']
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

        elif db_type == 'postgresql':
            host = config['host']
            port = config.get('port', 5432)
            user = config['user']
            password = config.get('password', '')
            database = config['database']
            return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        else:
            raise DatabaseError(f"Unsupported database type: {db_type}")

    def _create_database_tables(self) -> None:
        """Create database tables"""
        try:
            if not self.engine:
                raise DatabaseError("Database engine not initialized")

            Base.metadata.create_all(self.engine)
        except Exception as e:
            raise DatabaseError(f"Failed to create tables: {e}")

    def _sync_content_item(self, item: Dict[str, Any]) -> None:
        """Sync a single content item to database with change detection"""
        try:
            if not self.session_factory:
                raise DatabaseError("Database session factory not initialized")

            with self.session_factory() as session:
                # Ensure user exists
                if not self.current_user_id:
                    user = self._get_or_create_user(session)
                    self.current_user_id = str(user.id)  # Ensure UUID is stored as string

                if not self.current_user_id:
                    raise DatabaseError("Failed to get or create user")

                content_type = item['type']
                content_data = item['data']

                # Calculate content hash for change detection
                content_hash = self._calculate_item_content_hash(item)

                # Check if content has changed by comparing with stored hash
                if self._is_content_unchanged(session, item, content_hash):
                    self.debug(f"Content unchanged, skipping: {item['name']}")
                    self.sync_stats['skipped_count'] += 1
                    return

                # Sync based on content type
                if content_type == 'blog':
                    # Check if this is a translation (non-English content)
                    frontmatter = content_data.get('frontmatter', content_data)
                    language = frontmatter.get('language', 'en')

                    if language != 'en':
                        # This is translation content, find the main English post and add translation
                        self._sync_blog_translation_only(session, content_data, item)
                    else:
                        # This is main English content, create/update the blog post
                        self._sync_blog_post(session, content_data, item, content_hash)
                elif content_type == 'episode':
                    # Handle episode content as specialized blog posts with series
                    self._sync_episode(session, content_data, item, content_hash)
                elif content_type == 'projects':
                    self._sync_project(session, content_data, item, content_hash)
                elif content_type == 'ideas':
                    self._sync_idea(session, content_data, item, content_hash)
                elif content_type in ['updates', 'moment']:
                    self._sync_update(session, content_data, item, content_hash)
                elif content_type == 'resume':
                    self._sync_resume(session, content_data, item, content_hash)
                else:
                    self.warning(f"Unknown content type: {content_type}")
                    return

                session.commit()

        except Exception as e:
            if 'session' in locals():
                session.rollback()
            raise DatabaseError(f"Failed to sync content item: {e}")

    def _simulate_sync_item(self, item: Dict[str, Any]) -> None:
        """Simulate syncing an item (dry run)"""
        self.debug(f"[DRY RUN] Would sync {item['type']}: {item['name']}")

    def _simulate_cleanup_deleted_content(self, current_content_items: List[Dict[str, Any]]) -> None:
        """Simulate cleanup of deleted content files (dry run)"""
        try:
            if not self.session_factory:
                return

            with self.session_factory() as session:
                # Build sets of current content identifiers (same logic as actual cleanup)
                current_blog_slugs = set()
                current_project_slugs = set()
                current_idea_slugs = set()
                current_update_ids = set()

                for item in current_content_items:
                    content_type = item['type']
                    content_data = item['data']

                    if content_type == 'blog':
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = frontmatter.get('title', 'Untitled')
                        slug = frontmatter.get('slug', self._generate_slug(title))
                        current_blog_slugs.add(slug)

                    elif content_type == 'episode':
                        # Episodes are stored as blog posts with content_type=episode
                        main_entity = content_data.get('main_entity', {})
                        title = main_entity.get('title', 'Untitled Episode')
                        slug = main_entity.get('slug', self._generate_slug(title))
                        current_blog_slugs.add(slug)

                    elif content_type == 'projects':
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = content_data.get('title', frontmatter.get('title', 'Untitled Project'))
                        slug = content_data.get('slug', frontmatter.get('slug', self._generate_slug(title)))
                        current_project_slugs.add(slug)

                    elif content_type == 'ideas':
                        # Check for main_entity first (from folder parser), then frontmatter
                        main_entity = content_data.get('main_entity', {})
                        frontmatter = content_data.get('frontmatter', {})
                        idea_data = {**frontmatter, **main_entity}  # main_entity takes priority
                        title = idea_data.get('title', 'Untitled Idea')
                        slug = idea_data.get('slug', self._generate_slug(title))
                        current_idea_slugs.add(slug)

                    elif content_type in ['updates', 'moment']:
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = frontmatter.get('title', 'Untitled Update')
                        update_date = self._parse_date(frontmatter.get('date', datetime.utcnow().date()))
                        current_update_ids.add((title, update_date))

                # Find orphaned records that would be deleted
                orphan_count = 0

                # Check blog posts
                orphaned_blog_posts = session.query(BlogPost).filter(
                    ~BlogPost.slug.in_(current_blog_slugs) if current_blog_slugs else True
                ).all()
                for post in orphaned_blog_posts:
                    self.debug(f"[DRY RUN] Would delete orphaned blog post: {post.slug}")
                    orphan_count += 1

                # Check projects
                orphaned_projects = session.query(Project).filter(
                    ~Project.slug.in_(current_project_slugs) if current_project_slugs else True
                ).all()
                for project in orphaned_projects:
                    self.debug(f"[DRY RUN] Would delete orphaned project: {project.slug}")
                    orphan_count += 1

                # Check ideas
                orphaned_ideas = session.query(Idea).filter(
                    ~Idea.slug.in_(current_idea_slugs) if current_idea_slugs else True
                ).all()
                for idea in orphaned_ideas:
                    self.debug(f"[DRY RUN] Would delete orphaned idea: {idea.slug}")
                    orphan_count += 1

                # Check updates
                all_updates = session.query(RecentUpdate).all()
                for update in all_updates:
                    update_id = (update.title, update.date)
                    if update_id not in current_update_ids:
                        self.debug(f"[DRY RUN] Would delete orphaned update: {update.title} ({update.date})")
                        orphan_count += 1

                self.sync_stats['deleted_count'] = orphan_count
                if orphan_count > 0:
                    self.info(f"🗑️ [DRY RUN] Would clean up {orphan_count} orphaned database records")
                else:
                    self.debug("[DRY RUN] No orphaned records found to clean up")

        except Exception as e:
            self.error(f"Failed to simulate cleanup of deleted content: {e}")

    def _get_or_create_user(self, session: Session) -> User:
        """Get or create default user for content.
        More defensive than the previous version:
        1. Always look up by *username* first to avoid UNIQUE collisions.
        2. If a concurrent insert slipped through, catch IntegrityError,
           rollback and fetch the existing row instead of crashing.
        """
        # Workspace owner configuration (defaults to "admin")
        cfg = self.config_manager.load_config().get('workspace', {}).get('owner', {})
        username = cfg.get('username', 'admin')

        # 1) Try to fetch by username (UNIQUE)
        user: Optional[User] = session.query(User).filter_by(username=username).one_or_none()

        if user is None:
            # 2) Not found ‑> attempt to create
            user = User(
                username=username,
                email=cfg.get('email', 'admin@example.com'),
                password_hash=cfg.get('password_hash', 'default_hash'),
                first_name=cfg.get('first_name', 'Admin'),
                last_name=cfg.get('last_name', 'User'),
                is_active=True,
                is_admin=True,
            )
            session.add(user)
            try:
                session.flush()  # May raise IntegrityError if race condition
            except Exception as exc:
                # Rollback partial insert and fetch the existing record
                session.rollback()
                self.debug(f"Race creating user '{username}', fetching existing: {exc}")
                user = session.query(User).filter_by(username=username).one()

        return user

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        if not title:
            return 'untitled'

        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')

        return slug or 'untitled'

    def _parse_datetime(self, date_str: Union[str, datetime]) -> datetime:
        """Parse datetime from string or return datetime object"""
        if isinstance(date_str, datetime):
            return date_str

        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return datetime.utcnow()

        return datetime.utcnow()

    def _parse_date(self, date_str: Union[str, datetime, date, None]) -> Optional[date]:
        """Parse date from string"""
        if not date_str:
            return None

        if isinstance(date_str, date):
            return date_str

        if isinstance(date_str, datetime):
            return date_str.date()

        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None

        return None

    def _get_database_type(self) -> str:
        """Get database type for logging"""
        if isinstance(self.database_config, dict):
            return self.database_config.get('type', 'unknown')
        return 'custom'

    def save_sync_summary(self) -> None:
        """Save sync summary to cache file"""
        try:
            sync_summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'stats': self.sync_stats,
                'database_config': self.database_config if isinstance(self.database_config, dict) else 'custom',
                'dry_run': self.dry_run
            }

            silan_dir = self.config_manager.project_dir / '.silan'
            silan_dir.mkdir(exist_ok=True)  # Create .silan directory if it doesn't exist

            summary_file = silan_dir / 'last_sync.json'
            with open(summary_file, 'w') as f:
                json.dump(sync_summary, f, indent=2)

            self.debug(f"Sync summary saved to {summary_file}")

        except Exception as e:
            self.error(f"Failed to save sync summary: {e}")

    def _update_config_sync_metadata(self) -> None:
        """Update .silan-cache files with sync metadata after successful sync - hierarchical approach"""
        try:
            current_time = datetime.utcnow().isoformat()

            # Get all content items that were processed
            content_items = self.content_logic.get_all_content_for_sync()

            # Group items by collection type for hierarchical processing
            collections = {}
            for item in content_items:
                item_path = Path(item['path'])
                if item_path.is_file():
                    content_dir = item_path.parent
                else:
                    content_dir = item_path

                # Extract collection type from path (e.g., blog, projects, ideas)
                content_root = self.config_manager.project_dir / 'content'
                relative_path = content_dir.relative_to(content_root)
                collection_type = relative_path.parts[0] if relative_path.parts else 'unknown'

                if collection_type not in collections:
                    collections[collection_type] = []
                collections[collection_type].append((item, content_dir))

            # Update project-level configs first, then collection-level configs
            for collection_type, items in collections.items():
                collection_hash_data = []

                # 1. Update project-level configs
                for item, content_dir in items:
                    try:
                        project_config_path = content_dir / '.silan-cache'
                        if not project_config_path.exists():
                            continue

                        # Read and update project config
                        project_hash = self._update_single_config(project_config_path, item, current_time)
                        if project_hash:
                            collection_hash_data.append(project_hash)

                    except Exception as e:
                        self.warning(f"Failed to update project config for {item.get('name', 'unknown')}: {e}")

                # 2. Update collection-level config
                try:
                    collection_config_path = self.config_manager.project_dir / 'content' / collection_type / '.silan-cache'
                    if collection_config_path.exists():
                        # Calculate collection hash based on all project hashes
                        collection_hash = self._calculate_collection_hash(collection_hash_data)

                        # Create a dummy item for collection
                        collection_item = {
                            'name': f'{collection_type}_collection',
                            'path': str(collection_config_path.parent)
                        }

                        self._update_single_config(collection_config_path, collection_item, current_time, collection_hash)
                        self.debug(f"Updated collection config for {collection_type}")

                except Exception as e:
                    self.warning(f"Failed to update collection config for {collection_type}: {e}")

        except Exception as e:
            self.error(f"Failed to update config sync metadata: {e}")

    def _update_single_config(self, config_path: Path, item: Dict[str, Any], current_time: str, override_hash: str = None) -> str:
        """Update a single .silan-cache file and return its hash"""
        try:
            import yaml

            # Read current config
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if not config_data:
                return ""

            # Calculate hash for this config's content
            if override_hash:
                content_hash = override_hash
            else:
                item_with_dir_path = item.copy()
                item_with_dir_path['path'] = str(config_path.parent)
                content_hash = self._calculate_content_hash(item_with_dir_path)

            # Update sync metadata
            if 'sync_metadata' not in config_data:
                config_data['sync_metadata'] = {}

            config_data['sync_metadata'].update({
                'last_hash': content_hash,
                'last_sync_date': current_time,
                'sync_status': 'completed'
            })

            # Write updated config back
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            self.debug(f"Updated sync metadata for {item['name']}")
            return content_hash

        except Exception as e:
            self.warning(f"Failed to update single config {config_path}: {e}")
            return ""

    def _calculate_collection_hash(self, project_hashes: List[str]) -> str:
        """Calculate hash for a collection based on all project hashes within it"""
        try:
            if not project_hashes:
                return hashlib.sha256(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:16]

            # Sort hashes for consistent results
            sorted_hashes = sorted(project_hashes)
            combined_hash = ''.join(sorted_hashes)
            return hashlib.sha256(combined_hash.encode()).hexdigest()[:16]

        except Exception:
            return hashlib.sha256(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:16]

    def _calculate_content_hash(self, item: Dict[str, Any]) -> str:
        """Calculate hash of all content files for an item"""
        try:
            hash_obj = hashlib.sha256()

            item_path = Path(item['path'])

            # Get all content files (markdown, yaml, etc.)
            content_files = []
            for pattern in ['*.md', '*.yaml', '*.yml']:
                content_files.extend(item_path.glob(pattern))
                content_files.extend(item_path.glob(f'**/{pattern}'))

            # Sort for consistent hashing
            content_files.sort()

            for file_path in content_files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'rb') as f:
                            hash_obj.update(f.read())
                    except Exception:
                        # Skip files that can't be read
                        continue

            return hash_obj.hexdigest()[:16]  # First 16 chars

        except Exception:
            # Return a timestamp-based hash if calculation fails
            import time
            return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    def _calculate_item_content_hash(self, item: Dict[str, Any]) -> str:
        """Calculate hash for content item to detect changes"""
        try:
            # Create a consistent hash from the content data
            content_data = item.get('data', {})

            # Get the main content fields that matter for change detection
            hash_input = {}

            # Handle frontmatter with safe serialization
            if 'frontmatter' in content_data:
                hash_input['frontmatter'] = self._serialize_safe(content_data['frontmatter'])

            # Handle content
            if 'content' in content_data:
                hash_input['content'] = str(content_data['content'])

            # Handle any additional data fields with safe serialization
            for key in ['title', 'slug', 'description', 'github_url', 'demo_url',
                       'technologies', 'categories', 'tags', 'series']:
                if key in content_data:
                    hash_input[key] = self._serialize_safe(content_data[key])

            # Convert to string and hash using a safer approach
            content_str = self._dict_to_hash_string(hash_input)
            return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        except Exception as e:
            self.warning(f"Failed to calculate content hash for {item.get('name', 'unknown')}: {e}")
            # Return a timestamp-based hash as fallback
            import time
            return hashlib.sha256(str(time.time()).encode()).hexdigest()

    def _serialize_safe(self, obj: Any, depth: int = 0) -> Any:
        """Safely serialize objects, handling dates and circular references"""
        # Limit recursion depth
        if depth > 3:
            return str(type(obj).__name__)

        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            # Avoid circular references by limiting depth and excluding problematic keys
            safe_dict = {}
            excluded_keys = {'metadata', 'main_entity', 'details', 'content_files', 'project_info', 'sync_metadata', 'data'}
            for k, v in obj.items():
                key_str = str(k)
                if key_str not in excluded_keys and not key_str.startswith('_') and len(safe_dict) < 20:
                    try:
                        safe_dict[key_str] = self._serialize_safe(v, depth + 1)
                    except (ValueError, TypeError, RecursionError):
                        # Skip problematic values
                        safe_dict[key_str] = str(type(v).__name__)
            return safe_dict
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_safe(item, depth + 1) for item in obj[:5]]  # Limit list size
        else:
            try:
                obj_str = str(obj)
                return obj_str[:100] if isinstance(obj_str, str) else str(type(obj).__name__)
            except (ValueError, TypeError, UnicodeError):
                return str(type(obj).__name__)

    def _dict_to_hash_string(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to a consistent string for hashing"""
        try:
            import json
            return json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            # Fallback to string representation
            sorted_items = sorted(data.items())
            return str(sorted_items)

    def _is_content_unchanged(self, session: Session, item: Dict[str, Any], current_hash: str) -> bool:
        """Check if content has changed using file modification time and content comparison"""
        try:
            content_type = item['type']
            content_data = item['data']

            # Check file modification time from item metadata
            file_path = Path(item.get('path', ''))
            if not file_path.exists():
                return False

            file_stat = file_path.stat()
            current_mtime = datetime.fromtimestamp(file_stat.st_mtime)

            # Get the appropriate existing record based on content type
            existing_record = None
            if content_type == 'blog':
                frontmatter = content_data.get('frontmatter', content_data)
                title = frontmatter.get('title', 'Untitled')
                slug = frontmatter.get('slug', self._generate_slug(title))
                existing_record = session.query(BlogPost).filter_by(slug=slug).first()

            elif content_type == 'projects':
                frontmatter = content_data.get('frontmatter', content_data)
                title = content_data.get('title', frontmatter.get('title', 'Untitled Project'))
                slug = content_data.get('slug', frontmatter.get('slug', self._generate_slug(title)))
                existing_record = session.query(Project).filter_by(slug=slug).first()

            elif content_type == 'ideas':
                # Check for main_entity first (from folder parser), then frontmatter
                main_entity = content_data.get('main_entity', {})
                frontmatter = content_data.get('frontmatter', {})
                idea_data = {**frontmatter, **main_entity}  # main_entity takes priority
                title = idea_data.get('title', 'Untitled Idea')
                slug = idea_data.get('slug', self._generate_slug(title))
                existing_record = session.query(Idea).filter_by(slug=slug).first()

            elif content_type in ['updates', 'moment']:
                frontmatter = content_data.get('frontmatter', content_data)
                title = frontmatter.get('title', 'Untitled Update')
                update_date = self._parse_date(frontmatter.get('date', datetime.utcnow().date()))
                existing_record = session.query(RecentUpdate).filter(
                    and_(
                        RecentUpdate.title == title,
                        RecentUpdate.date == update_date
                    )
                ).first()

            # If record doesn't exist, it's new content
            if not existing_record:
                return False

            # Check if file was modified after the last database update
            if hasattr(existing_record, 'updated_at') and existing_record.updated_at:
                # Ensure both timestamps are timezone-naive for comparison
                db_updated_at = existing_record.updated_at
                if db_updated_at.tzinfo is not None:
                    db_updated_at = db_updated_at.replace(tzinfo=None)

                if current_mtime.tzinfo is not None:
                    current_mtime = current_mtime.replace(tzinfo=None)

                # If file was modified after the last DB update, content has changed
                if current_mtime > db_updated_at:
                    self.debug(f"File {file_path.name} modified after last sync: {current_mtime} > {db_updated_at}")
                    return False

            # Additional check: compare key content fields for substantial changes
            # This helps catch cases where updated_at might not be reliable
            if self._has_substantial_content_changes(existing_record, content_data, content_type):
                self.debug(f"Substantial content changes detected for {item.get('name', 'unknown')}")
                return False

            # Content appears unchanged
            self.debug(f"Content unchanged for {item.get('name', 'unknown')}")
            return True

        except Exception as e:
            self.warning(f"Failed to check content changes for {item.get('name', 'unknown')}: {e}")
            # If we can't determine, assume it has changed to be safe
            return False

    def _has_substantial_content_changes(self, existing_record: Any, content_data: Dict[str, Any], content_type: str) -> bool:
        """Check if there are substantial changes in key content fields"""
        try:
            if content_type == 'blog':
                frontmatter = content_data.get('frontmatter', content_data)
                content = content_data.get('content', '')

                # Check title and content changes
                if (existing_record.title != frontmatter.get('title', 'Untitled') or
                    (existing_record.content or '') != content):
                    return True

            elif content_type == 'projects':
                frontmatter = content_data.get('frontmatter', content_data)
                title = content_data.get('title', frontmatter.get('title', 'Untitled Project'))
                description = content_data.get('description', frontmatter.get('description', ''))

                if (existing_record.title != title or
                    (existing_record.description or '') != description):
                    return True

            elif content_type == 'ideas':
                frontmatter = content_data.get('frontmatter', content_data)
                title = frontmatter.get('title', 'Untitled Idea')
                abstract = frontmatter.get('abstract', frontmatter.get('description', ''))

                if (existing_record.title != title or
                    (existing_record.abstract or '') != abstract):
                    return True

            elif content_type in ['updates', 'moment']:
                frontmatter = content_data.get('frontmatter', content_data)
                content = content_data.get('content', '')
                description = content or frontmatter.get('description', '')

                if (existing_record.description or '') != description:
                    return True

            return False

        except Exception as e:
            self.warning(f"Failed to check substantial changes: {e}")
            # If we can't determine, assume there are changes
            return True

    def _display_sync_results(self) -> None:
        """Display comprehensive sync results"""
        try:
            # Summary statistics
            stats_data = {
                "Total Items": self.sync_stats['total_items'],
                "Successfully Processed": self.sync_stats['success_count'],
                "Created": self.sync_stats['created_count'],
                "Updated": self.sync_stats['updated_count'],
                "Skipped": self.sync_stats['skipped_count'],
                "Deleted": self.sync_stats['deleted_count'],
                "Errors": self.sync_stats['error_count']
            }

            if self.dry_run:
                self.cli.display_info_panel("Dry Run Results", stats_data)
            else:
                self.cli.display_success_panel(
                    "Sync Completed Successfully",
                    "Database synchronization completed",
                    stats_data
                )

            # Show errors if any
            if self.sync_stats['sync_errors']:
                self.error("Synchronization errors occurred:")
                for i, error in enumerate(self.sync_stats['sync_errors'][:5]):
                    self.error(f"  {i+1}. {error}")

            # Show warnings if any
            if self.sync_stats['sync_warnings']:
                self.warning(f"Sync completed with {len(self.sync_stats['sync_warnings'])} warnings")

        except Exception as e:
            self.error(f"Failed to display sync results: {e}")

    def _cleanup_deleted_content(self, current_content_items: List[Dict[str, Any]]) -> None:
        """Clean up database records for deleted content files"""
        try:
            if not self.session_factory:
                return

            with self.session_factory() as session:
                # Build sets of current content identifiers
                current_blog_slugs = set()
                current_project_slugs = set()
                current_idea_slugs = set()
                current_update_ids = set()

                for item in current_content_items:
                    content_type = item['type']
                    content_data = item['data']

                    if content_type == 'blog':
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = frontmatter.get('title', 'Untitled')
                        slug = frontmatter.get('slug', self._generate_slug(title))
                        current_blog_slugs.add(slug)

                    elif content_type == 'episode':
                        # Episodes are stored as blog posts with content_type=episode
                        main_entity = content_data.get('main_entity', {})
                        title = main_entity.get('title', 'Untitled Episode')
                        slug = main_entity.get('slug', self._generate_slug(title))
                        current_blog_slugs.add(slug)

                    elif content_type == 'projects':
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = content_data.get('title', frontmatter.get('title', 'Untitled Project'))
                        slug = content_data.get('slug', frontmatter.get('slug', self._generate_slug(title)))
                        current_project_slugs.add(slug)

                    elif content_type == 'ideas':
                        # Check for main_entity first (from folder parser), then frontmatter
                        main_entity = content_data.get('main_entity', {})
                        frontmatter = content_data.get('frontmatter', {})
                        idea_data = {**frontmatter, **main_entity}  # main_entity takes priority
                        title = idea_data.get('title', 'Untitled Idea')
                        slug = idea_data.get('slug', self._generate_slug(title))
                        current_idea_slugs.add(slug)

                    elif content_type in ['updates', 'moment']:
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = frontmatter.get('title', 'Untitled Update')
                        update_date = self._parse_date(frontmatter.get('date', datetime.utcnow().date()))
                        current_update_ids.add((title, update_date))

                # Find and delete orphaned records
                deleted_count = 0

                # Clean up blog posts
                orphaned_blog_posts = session.query(BlogPost).filter(
                    ~BlogPost.slug.in_(current_blog_slugs) if current_blog_slugs else True
                ).all()

                for post in orphaned_blog_posts:
                    self.debug(f"Deleting orphaned blog post: {post.slug}")
                    # Delete related records first (tags, translations, etc.)
                    session.query(BlogPostTag).filter_by(blog_post_id=post.id).delete()
                    session.query(BlogPostTranslation).filter_by(blog_post_id=post.id).delete()
                    session.delete(post)
                    deleted_count += 1

                # Clean up projects
                orphaned_projects = session.query(Project).filter(
                    ~Project.slug.in_(current_project_slugs) if current_project_slugs else True
                ).all()

                for project in orphaned_projects:
                    self.debug(f"Deleting orphaned project: {project.slug}")
                    # Delete related records first
                    session.query(ProjectTechnology).filter_by(project_id=project.id).delete()
                    session.query(ProjectDetail).filter_by(project_id=project.id).delete()
                    session.delete(project)
                    deleted_count += 1

                # Clean up ideas
                orphaned_ideas = session.query(Idea).filter(
                    ~Idea.slug.in_(current_idea_slugs) if current_idea_slugs else True
                ).all()

                for idea in orphaned_ideas:
                    self.debug(f"Deleting orphaned idea: {idea.slug}")
                    session.delete(idea)
                    deleted_count += 1

                # Clean up updates/moments
                all_updates = session.query(RecentUpdate).all()
                for update in all_updates:
                    update_id = (update.title, update.date)
                    if update_id not in current_update_ids:
                        self.debug(f"Deleting orphaned update: {update.title} ({update.date})")
                        session.delete(update)
                        deleted_count += 1

                if deleted_count > 0:
                    session.commit()
                    self.sync_stats['deleted_count'] = deleted_count
                    self.info(f"🗑️ Cleaned up {deleted_count} orphaned database records")
                else:
                    self.debug("No orphaned records found to clean up")

        except Exception as e:
            self.error(f"Failed to cleanup deleted content: {e}")
            if 'session' in locals():
                session.rollback()

    def _cleanup_database(self) -> None:
        """Clean up database resources"""
        try:
            if self.engine:
                self.engine.dispose()
                self.debug("Database connection disposed")
        except Exception as e:
            self.error(f"Error during database cleanup: {e}")

    def cleanup(self) -> None:
        """Clean up all resources"""
        self._cleanup_database()
        if self.content_logic:
            self.content_logic.cleanup()
