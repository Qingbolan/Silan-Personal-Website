"""Database synchronization business logic implementation"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Union, List, Optional, cast
from datetime import datetime, date
from rich.progress import TaskID
from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker, Session

from ..core.exceptions import DatabaseError, ValidationError
from ..models import (
    Base, User, BlogPost, BlogTag, BlogPostTag, BlogPostTranslation,
    BlogCategory, BlogSeries, BlogSeriesTranslation, Comment, CommentLike, Project, ProjectTechnology,
    ProjectDetail, Idea, RecentUpdate, UpdateType, UpdateStatus, UpdatePriority, PersonalInfo,
    Education, EducationDetail, WorkExperience, WorkExperienceDetail, Award, Publication, PublicationAuthor,
    ResearchProject, ResearchProjectDetail, SocialLink, UserIdentity
)
from ..utils import ModernLogger, CLIInterface, FileOperations, ConfigManager
from .content_logic import ContentLogic


class DatabaseSyncLogger(ModernLogger):
    """Specialized logger for database sync operations"""
    
    def __init__(self):
        super().__init__(name="db_sync", level="info")
    
    def sync_start(self, db_type: str, content_count: int) -> None:
        """Log sync operation start"""
        self.stage(f"Starting sync to {db_type} database")
        self.info(f"📚 Found {content_count} content items to process")
    
    def sync_progress(self, current: int, total: int, item_name: str) -> None:
        """Log sync progress"""
        self.debug(f"Syncing ({current}/{total}): {item_name}")
    
    def sync_complete(self, success_count: int, error_count: int) -> None:
        """Log sync completion"""
        if error_count == 0:
            self.success(f"✅ Sync completed: {success_count} items processed successfully")
        else:
            self.warning(f"⚠️ Sync completed with {error_count} errors: {success_count} success, {error_count} failed")


class DatabaseSyncLogic(DatabaseSyncLogger):
    """Complex business logic for database synchronization"""
    
    def __init__(self, database_config: Union[str, Dict[str, Any]], dry_run: bool = False):
        super().__init__()
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
    
    def validate_configuration(self) -> bool:
        """Validate database configuration"""
        try:
            if isinstance(self.database_config, dict):
                self._validate_database_dict(self.database_config)
            elif isinstance(self.database_config, str):
                if not self.database_config.strip():
                    raise ValidationError("Database connection string cannot be empty")
            else:
                raise ValidationError("Database config must be dict or string")
            
            return True
            
        except ValidationError as e:
            self.error(f"Configuration validation failed: {e}")
            return False
    
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
            self.info("✅ Database tables created/verified")
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
    
    def _sync_blog_post(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync blog post to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')
            
            # Required fields
            title = frontmatter.get('title', 'Untitled')
            slug = frontmatter.get('slug', self._generate_slug(title))
            
            # Extract content_type from both locations
            content_type = content_data.get('content_type', frontmatter.get('content_type', frontmatter.get('type', 'article')))
            
            # Map content_type to valid database enum values
            content_type_mapping = {
                'article': 'article',
                'vlog': 'vlog', 
                'tutorial': 'tutorial',
                'podcast': 'podcast',
                # Handle variations
                'video': 'vlog',
                'howto': 'tutorial',
                'how-to': 'tutorial'
            }
            content_type = content_type_mapping.get(content_type.lower(), 'article')
            
            # Determine status more intelligently
            status = self._determine_blog_status(frontmatter, content_data)
            
            # Check if blog post exists
            existing_post = session.query(BlogPost).filter_by(slug=slug).first()
            
            if existing_post:
                # Update existing post only if content has changed
                from ..models.blog import BlogStatus, BlogContentType
                existing_post.title = title
                existing_post.content = content
                existing_post.excerpt = frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', '')))
                existing_post.is_featured = frontmatter.get('featured', False)
                existing_post.content_type = BlogContentType(content_type.lower())
                existing_post.status = BlogStatus(status.lower())
                existing_post.updated_at = datetime.utcnow()

                # Handle view and like counts
                existing_post.view_count = frontmatter.get('views', existing_post.view_count)
                existing_post.like_count = frontmatter.get('likes', existing_post.like_count)

                if frontmatter.get('date'):
                    existing_post.published_at = self._parse_datetime(frontmatter['date'])

                # Content updated, the updated_at timestamp will be set automatically

                blog_post = existing_post
                self.sync_stats['updated_count'] += 1
            else:
                # Create new post
                from ..models.blog import BlogStatus, BlogContentType
                assert self.current_user_id is not None
                blog_post_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'slug': slug,
                    'content': content,
                    'excerpt': frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', ''))),
                    'is_featured': frontmatter.get('featured', False),
                    'content_type': BlogContentType(content_type.lower()),
                    'status': BlogStatus(status.lower()),
                    'view_count': frontmatter.get('views', 0),
                    'like_count': frontmatter.get('likes', 0),
                    'published_at': self._parse_datetime(frontmatter.get('date', datetime.utcnow()))
                }

                # New blog post will have created_at timestamp set automatically

                blog_post = BlogPost(**blog_post_data)
                session.add(blog_post)
                session.flush()  # Get the ID
                self.sync_stats['created_count'] += 1
            
            # Handle tags - check both frontmatter and top-level content_data
            tags_to_sync = None
            if 'tags' in frontmatter and frontmatter['tags']:
                tags_to_sync = frontmatter['tags']
            elif 'tags' in content_data and content_data['tags']:
                tags_to_sync = content_data['tags']
            
            if tags_to_sync:
                self._sync_blog_tags(session, blog_post, tags_to_sync)
            
            # Handle categories - check both frontmatter and top-level content_data
            categories_to_sync = None
            if 'categories' in frontmatter and frontmatter['categories']:
                categories_to_sync = frontmatter['categories']
            elif 'categories' in content_data and content_data['categories']:
                categories_to_sync = content_data['categories']
            
            if categories_to_sync:
                self._sync_blog_categories(session, blog_post, categories_to_sync)
            
            # Handle series - check both frontmatter and top-level content_data
            series_to_sync = None
            if 'series' in frontmatter and frontmatter['series']:
                series_to_sync = frontmatter['series']
            elif 'series' in content_data and content_data['series']:
                series_to_sync = content_data['series']
            
            if series_to_sync:
                self._sync_blog_series(session, blog_post, series_to_sync)
            
            # Handle translations - check if this content has language variants
            self._sync_blog_translations(session, blog_post, content_data, item)
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync blog post: {e}")
    
    def _determine_blog_status(self, frontmatter: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """Determine blog post status intelligently"""
        # Check explicit status field
        status = frontmatter.get('status', content_data.get('status', '')).lower()
        
        # Check published field
        published = frontmatter.get('published', content_data.get('published', True))
        
        # Check if it's in drafts folder
        path = content_data.get('path', '')
        if 'drafts' in path.lower():
            return 'draft'
        
        # Status mapping
        if status in ['draft', 'unpublished', 'private']:
            return 'draft'
        elif status in ['published', 'public']:
            return 'published'
        elif status in ['archived']:
            return 'archived'
        elif not published:
            return 'draft'
        else:
            return 'published'
    
    def _sync_blog_series(self, session: Session, blog_post: BlogPost, series_data: Any) -> None:
        """Sync blog series information"""
        try:
            from ..models.blog import BlogSeries, BlogPost
            
            # Handle different series data formats
            if isinstance(series_data, dict):
                series_name = series_data.get('name', '')
                series_description = series_data.get('description', '')
                part_number = series_data.get('part', series_data.get('part_number', 1))
            elif isinstance(series_data, str):
                series_name = series_data
                series_description = ''
                part_number = 1
            else:
                return
            
            if not series_name:
                return
            
            # Generate series slug
            series_slug = self._generate_slug(series_name)
            
            # Get or create series
            series = session.query(BlogSeries).filter_by(slug=series_slug).first()
            if not series:
                series = BlogSeries(
                    title=series_name,
                    slug=series_slug,
                    description=series_description
                )
                session.add(series)
                session.flush()
            
            # Update blog post with series info
            blog_post.series_id = series.id
            blog_post.series_order = part_number
            
            # Update episode count for the series
            episode_count = session.query(BlogPost).filter_by(series_id=series.id).count()
            series.episode_count = episode_count
            
        except Exception as e:
            self.warning(f"Failed to sync blog series: {e}")
    
    def _sync_project(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync project to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')
            
            # Use top-level content_data fields (from parser) rather than nested frontmatter
            title = content_data.get('title', frontmatter.get('title', 'Untitled Project'))
            slug = content_data.get('slug', frontmatter.get('slug', self._generate_slug(title)))
            description = content_data.get('description', frontmatter.get('description', ''))
            github_url = content_data.get('github_url', frontmatter.get('github_url', ''))
            demo_url = content_data.get('demo_url', frontmatter.get('demo_url', ''))
            is_featured = content_data.get('is_featured', frontmatter.get('featured', False))
            start_date = content_data.get('start_date', frontmatter.get('start_date'))
            end_date = content_data.get('end_date', frontmatter.get('end_date'))
            
            # Check if project exists
            existing_project = session.query(Project).filter_by(slug=slug).first()
            
            if existing_project:
                # Update existing project
                existing_project.title = title
                existing_project.description = description
                existing_project.github_url = github_url
                existing_project.demo_url = demo_url
                existing_project.is_featured = is_featured
                existing_project.is_public = True  # Set as public so it shows in API
                existing_project.updated_at = datetime.utcnow()

                if start_date:
                    existing_project.start_date = self._parse_date(start_date)
                if end_date:
                    existing_project.end_date = self._parse_date(end_date)

                # Content updated, the updated_at timestamp will be set automatically

                project = existing_project
                self.sync_stats['updated_count'] += 1
            else:
                # Create new project
                assert self.current_user_id is not None
                project_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'slug': slug,
                    'description': description,
                    'github_url': github_url,
                    'demo_url': demo_url,
                    'is_featured': is_featured,
                    'is_public': True,  # Set as public so it shows in API
                    'start_date': self._parse_date(start_date),
                    'end_date': self._parse_date(end_date)
                }

                # New project will have created_at timestamp set automatically

                project = Project(**project_data)
                session.add(project)
                session.flush()
                self.sync_stats['created_count'] += 1
            
            # Handle technologies - check both top-level and frontmatter
            technologies_data = content_data.get('technologies', frontmatter.get('technologies', []))
            if technologies_data:
                # Convert structured technology data to simple list of names
                if isinstance(technologies_data, list) and len(technologies_data) > 0:
                    if isinstance(technologies_data[0], dict):
                        # Convert from [{"technology_name": "React", ...}, ...] to ["React", ...]
                        tech_names = [tech.get('technology_name', str(tech)) for tech in technologies_data if tech]
                    else:
                        # Already a simple list
                        tech_names = technologies_data
                    self._sync_project_technologies(session, project, tech_names)
            
            # Handle project details (README content, license, version)
            license_str = None
            version_str = None
            license_text = None
            try:
                # Check if we have parsed metadata with details (from project parser)
                metadata = content_data.get('metadata', {})
                details_meta = metadata.get('details', []) if isinstance(metadata, dict) else []

                # If we have details from parser, use them
                if isinstance(details_meta, list) and details_meta and isinstance(details_meta[0], dict):
                    license_str = details_meta[0].get('license')
                    version_str = details_meta[0].get('version')
                    license_text = details_meta[0].get('license_text')

                # Also check main_entity from parser (where license is also stored)
                main_entity = content_data.get('main_entity', {})
                if isinstance(main_entity, dict):
                    license_str = license_str or main_entity.get('license')
                    license_text = license_text or main_entity.get('license_text')
                    version_str = version_str or main_entity.get('version')

                # Fallbacks from top-level parsed fields or frontmatter
                license_str = content_data.get('license', license_str) or (frontmatter.get('license') if isinstance(frontmatter, dict) else None) or license_str
                version_str = content_data.get('version', version_str) or (frontmatter.get('version') if isinstance(frontmatter, dict) else None) or version_str
                license_text = content_data.get('license_text', license_text) or (frontmatter.get('license_text') if isinstance(frontmatter, dict) else None) or license_text
            except Exception:
                pass

            if content or license_str or version_str or license_text:
                self._sync_project_details(session, project, content, license_str, license_text, version_str)

        except Exception as e:
            raise DatabaseError(f"Failed to sync project: {e}")
    
    def _sync_idea(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync idea to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')
            
            title = frontmatter.get('title', 'Untitled Idea')
            slug = frontmatter.get('slug', self._generate_slug(title))
            
            # Check if idea exists
            existing_idea = session.query(Idea).filter_by(slug=slug).first()
            
            if existing_idea:
                # Update existing idea
                existing_idea.title = title
                existing_idea.abstract = frontmatter.get('abstract', frontmatter.get('description', ''))
                existing_idea.is_public = True  # Set as public so it shows in API
                existing_idea.updated_at = datetime.utcnow()

                # Content updated, the updated_at timestamp will be set automatically

                idea = existing_idea
                self.sync_stats['updated_count'] += 1
            else:
                # Create new idea
                assert self.current_user_id is not None
                idea_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'slug': slug,
                    'abstract': frontmatter.get('abstract', frontmatter.get('description', '')),
                    'motivation': content if content else None,
                    'is_public': True  # Set as public so it shows in API
                }

                # New idea will have created_at timestamp set automatically

                idea = Idea(**idea_data)
                session.add(idea)
                session.flush()
                self.sync_stats['created_count'] += 1
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync idea: {e}")
    
    def _sync_update(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync update/moment to database with rich fields (type/status/tags/priority)."""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')

            # Basic fields
            title = frontmatter.get('title', 'Untitled Update')
            update_date = self._parse_date(frontmatter.get('date', datetime.utcnow().date()))
            description = content or frontmatter.get('description', '')

            # Map enums safely
            def _map_update_type(val: Optional[str]) -> UpdateType:
                if not val:
                    return UpdateType.PROJECT
                v = str(val).lower()
                mapping = {
                    'work': UpdateType.WORK,
                    'education': UpdateType.EDUCATION,
                    'research': UpdateType.RESEARCH,
                    'publication': UpdateType.PUBLICATION,
                    'project': UpdateType.PROJECT,
                }
                return mapping.get(v, UpdateType.PROJECT)

            def _map_status(val: Optional[str]) -> UpdateStatus:
                if not val:
                    return UpdateStatus.ACTIVE
                v = str(val).lower()
                mapping = {
                    'active': UpdateStatus.ACTIVE,
                    'ongoing': UpdateStatus.ONGOING,
                    'completed': UpdateStatus.COMPLETED,
                }
                return mapping.get(v, UpdateStatus.ACTIVE)

            def _map_priority(val: Optional[str]) -> UpdatePriority:
                if not val:
                    return UpdatePriority.MEDIUM
                v = str(val).lower()
                mapping = {
                    'high': UpdatePriority.HIGH,
                    'medium': UpdatePriority.MEDIUM,
                    'low': UpdatePriority.LOW,
                }
                return mapping.get(v, UpdatePriority.MEDIUM)

            # Collect metadata
            update_type = _map_update_type(frontmatter.get('type') or content_data.get('type') or content_data.get('update_type'))
            status = _map_status(frontmatter.get('status') or content_data.get('status'))
            priority = _map_priority(frontmatter.get('priority') or content_data.get('priority'))
            tags = frontmatter.get('tags') or content_data.get('tags') or []
            if isinstance(tags, str):
                tags = [tags]

            # Optional links/media
            github_url = frontmatter.get('github_url') or frontmatter.get('github')
            demo_url = frontmatter.get('demo_url') or frontmatter.get('demo')
            external_url = frontmatter.get('external_url') or frontmatter.get('link')

            # Check if update exists (by title and date)
            existing_update = session.query(RecentUpdate).filter(
                and_(
                    RecentUpdate.title == title,
                    RecentUpdate.date == update_date
                )
            ).first()

            if existing_update:
                # Update existing
                existing_update.description = description
                existing_update.type = update_type
                existing_update.status = status
                existing_update.priority = priority
                existing_update.tags = tags
                existing_update.github_url = github_url
                existing_update.demo_url = demo_url
                existing_update.external_url = external_url
                existing_update.updated_at = datetime.utcnow()

                # Content updated, the updated_at timestamp will be set automatically

                update = existing_update
                self.sync_stats['updated_count'] += 1
            else:
                # Create new
                assert self.current_user_id is not None
                update_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'description': description,
                    'date': update_date,
                    'type': update_type,
                    'status': status,
                    'priority': priority,
                    'tags': tags,
                    'github_url': github_url,
                    'demo_url': demo_url,
                    'external_url': external_url,
                }

                # New update will have created_at timestamp set automatically

                update = RecentUpdate(**update_data)
                session.add(update)
                session.flush()
                self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync update: {e}")

    def _sync_resume(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync resume to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')
            
            # Upsert personal info instead of delete+recreate
            assert self.current_user_id is not None
            existing_pi = session.query(PersonalInfo).filter_by(user_id=self.current_user_id, is_primary=True).first()
            if existing_pi:
                existing_pi.full_name = frontmatter.get('name', frontmatter.get('full_name', existing_pi.full_name or 'Unknown'))
                existing_pi.title = frontmatter.get('title', frontmatter.get('current_position', existing_pi.title or 'Professional'))
                existing_pi.current_status = frontmatter.get('current', frontmatter.get('bio', frontmatter.get('summary', existing_pi.current_status or '')))
                existing_pi.location = frontmatter.get('location', existing_pi.location or '')
                existing_pi.email = frontmatter.get('email', existing_pi.email or '')
                existing_pi.phone = frontmatter.get('phone', existing_pi.phone or '')
                existing_pi.website = frontmatter.get('website', existing_pi.website or '')
                existing_pi.avatar_url = frontmatter.get('profile_image', frontmatter.get('avatar_url', existing_pi.avatar_url or ''))
                personal_info = existing_pi
                self.sync_stats['updated_count'] += 1
            else:
                personal_info = PersonalInfo(
                    user_id=self.current_user_id,
                    full_name=frontmatter.get('name', frontmatter.get('full_name', 'Unknown')),
                    title=frontmatter.get('title', frontmatter.get('current_position', 'Professional')),
                    current_status=frontmatter.get('current', frontmatter.get('bio', frontmatter.get('summary', ''))),
                    location=frontmatter.get('location', ''),
                    email=frontmatter.get('email', ''),
                    phone=frontmatter.get('phone', ''),
                    website=frontmatter.get('website', ''),
                    avatar_url=frontmatter.get('profile_image', frontmatter.get('avatar_url', '')),
                    is_primary=True
                )
                session.add(personal_info)
                session.flush()
                self.sync_stats['created_count'] += 1

            # Upsert education records
            education_data = content_data.get('education', [])
            self._sync_education(session, education_data)

            # Upsert work experience records (also handles details inside)
            experience_data = content_data.get('experience', [])
            self._sync_work_experience(session, experience_data)

            # Upsert awards if present
            awards_data = content_data.get('awards', [])
            if awards_data:
                self._sync_awards(session, awards_data)

            self.debug("Resume sync completed (upsert version)")
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync resume: {e}")

    def _delete_all_resume_records(self, session: Session) -> None:
        """Delete all resume-related records for clean recreation using SQL"""
        try:
            # 使用原生SQL避免UUID对象问题
            from sqlalchemy import text

            # 按外键依赖顺序删除：子表 -> 父表
            # 删除所有resume相关表的所有记录（简单粗暴）
            session.execute(text("DELETE FROM education_details"))
            session.execute(text("DELETE FROM work_experience_details"))
            session.execute(text("DELETE FROM publication_authors"))
            session.execute(text("DELETE FROM research_project_details"))
            session.execute(text("DELETE FROM education"))
            session.execute(text("DELETE FROM work_experience"))
            session.execute(text("DELETE FROM awards"))
            session.execute(text("DELETE FROM publications"))
            session.execute(text("DELETE FROM research_projects"))
            session.execute(text("DELETE FROM social_links"))
            session.execute(text("DELETE FROM personal_info"))

            session.flush()
            self.debug("Successfully deleted all existing resume records using SQL")

        except Exception as e:
            self.warning(f"Failed to delete resume records: {e}")
            # 不抛出异常，继续执行创建操作

    def _sync_education(self, session: Session, education_data: List[Dict[str, Any]]) -> None:
        """Sync education data to database"""
        for edu_item in education_data:
            # Check if education record exists
            existing_education = session.query(Education).filter_by(
                user_id=self.current_user_id,
                institution=edu_item.get('institution', ''),
                degree=edu_item.get('degree', '')
            ).first()
            
            if existing_education:
                # Update existing education
                existing_education.field_of_study = edu_item.get('field_of_study', '')
                existing_education.start_date = self._parse_date(edu_item.get('start_date'))
                existing_education.end_date = self._parse_date(edu_item.get('end_date'))
                existing_education.is_current = edu_item.get('is_current', False)
                existing_education.gpa = edu_item.get('gpa')
                existing_education.location = edu_item.get('location', '')
                existing_education.institution_website = edu_item.get('institution_website', '')
                existing_education.institution_logo_url = edu_item.get('institution_logo_url', '')
                existing_education.updated_at = datetime.utcnow()
                
                education = existing_education
                self.sync_stats['updated_count'] += 1
            else:
                # Create new education record
                education = Education(
                    user_id=self.current_user_id,
                    institution=edu_item.get('institution', ''),
                    degree=edu_item.get('degree', ''),
                    field_of_study=edu_item.get('field_of_study', ''),
                    start_date=self._parse_date(edu_item.get('start_date')),
                    end_date=self._parse_date(edu_item.get('end_date')),
                    is_current=edu_item.get('is_current', False),
                    gpa=edu_item.get('gpa'),
                    location=edu_item.get('location', ''),
                    institution_website=edu_item.get('institution_website', ''),
                    institution_logo_url=edu_item.get('institution_logo_url', ''),
                    sort_order=len(session.query(Education).filter_by(user_id=self.current_user_id).all())
                )
                session.add(education)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(education)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1
            
            # Sync education details if present
            details = edu_item.get('details', [])
            if details:
                session.flush()
                session.refresh(education)
                # Now sync education details
                self._sync_education_details(session, education, details)
    
    def _sync_work_experience(self, session: Session, experience_data: List[Dict[str, Any]]) -> None:
        """Sync work experience data to database"""
        for exp_item in experience_data:
            # Check if work experience record exists
            existing_experience = session.query(WorkExperience).filter_by(
                user_id=self.current_user_id,
                company=exp_item.get('company', ''),
                position=exp_item.get('position', '')
            ).first()
            
            if existing_experience:
                # Update existing experience
                existing_experience.start_date = self._parse_date(exp_item.get('start_date'))
                existing_experience.end_date = self._parse_date(exp_item.get('end_date'))
                existing_experience.is_current = exp_item.get('is_current', False)
                existing_experience.location = exp_item.get('location', '')
                existing_experience.company_website = exp_item.get('company_website', '')
                existing_experience.company_logo_url = exp_item.get('company_logo_url', '')
                existing_experience.updated_at = datetime.utcnow()
                
                work_experience = existing_experience
                self.sync_stats['updated_count'] += 1
            else:
                # Create new work experience record
                work_experience = WorkExperience(
                    user_id=self.current_user_id,
                    company=exp_item.get('company', ''),
                    position=exp_item.get('position', ''),
                    start_date=self._parse_date(exp_item.get('start_date')),
                    end_date=self._parse_date(exp_item.get('end_date')),
                    is_current=exp_item.get('is_current', False),
                    location=exp_item.get('location', ''),
                    company_website=exp_item.get('company_website', ''),
                    company_logo_url=exp_item.get('company_logo_url', ''),
                    sort_order=len(session.query(WorkExperience).filter_by(user_id=self.current_user_id).all())
                )
                session.add(work_experience)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(work_experience)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1
            
            # Sync work experience details immediately after creating the record
            details = exp_item.get('details', [])
            if details:
                # Flush instead of commit to keep all inserts in one transaction
                session.flush()
                session.refresh(work_experience)
                # Now sync work experience details
                self._sync_work_experience_details(session, work_experience, details)
    
    def _sync_awards(self, session: Session, awards_data: List[Dict[str, Any]]) -> None:
        """Sync awards data to database"""
        for award_item in awards_data:
            # Check if award record exists
            existing_award = session.query(Award).filter_by(
                user_id=self.current_user_id,
                title=award_item.get('title', ''),
                awarding_organization=award_item.get('awarding_organization', award_item.get('issuer', ''))
            ).first()
            
            if existing_award:
                # Update existing award
                existing_award.award_date = self._parse_date(award_item.get('award_date'))
                existing_award.description = award_item.get('description', '')
                existing_award.updated_at = datetime.utcnow()
                self.sync_stats['updated_count'] += 1
            else:
                # Create new award record
                award = Award(
                    user_id=self.current_user_id,
                    title=award_item.get('title', ''),
                    awarding_organization=award_item.get('awarding_organization', award_item.get('issuer', '')),
                    award_date=self._parse_date(award_item.get('award_date')),
                    description=award_item.get('description', ''),
                    sort_order=len(session.query(Award).filter_by(user_id=self.current_user_id).all())
                )
                session.add(award)
                self.sync_stats['created_count'] += 1
    
    def _sync_education_details(self, session: Session, education: Education, details: List[str]) -> None:
        """Sync education details to database"""
        
        # Check if details already exist
        existing_count = session.query(EducationDetail).filter(
            EducationDetail.education_id == education.id
        ).count()
        
        if existing_count > 0:
            return
        
        # Create new details
        for i, detail_text in enumerate(details):
            if not detail_text or not detail_text.strip():
                continue
                
            try:
                education_detail = EducationDetail(
                    education_id=education.id,
                    detail_text=detail_text.strip(),
                    sort_order=i
                )
                session.add(education_detail)
                # Force individual insert to avoid insertmanyvalues bulk processing
                session.flush()
                self.sync_stats['created_count'] += 1
            except Exception as e:
                self.warning(f"Failed to create education detail: {e}")
                continue
    
    def _sync_work_experience_details(self, session: Session, work_experience: WorkExperience, details: List[str]) -> None:
        """Sync work experience details to database"""
        
        # Check if details already exist
        existing_count = session.query(WorkExperienceDetail).filter(
            WorkExperienceDetail.work_experience_id == work_experience.id
        ).count()
        
        if existing_count > 0:
            return
        
        # Create new details
        for i, detail_text in enumerate(details):
            if not detail_text or not detail_text.strip():
                continue
                
            try:
                work_experience_detail = WorkExperienceDetail(
                    work_experience_id=work_experience.id,
                    detail_text=detail_text.strip(),
                    sort_order=i
                )
                session.add(work_experience_detail)
                # Force individual insert to avoid insertmanyvalues bulk processing
                session.flush()
                self.sync_stats['created_count'] += 1
            except Exception as e:
                self.warning(f"Failed to create work experience detail: {e}")
                continue
    
    def _sync_publications(self, session: Session, publications_data: List[Dict[str, Any]]) -> None:
        """Sync publications data to database"""
        for pub_item in publications_data:
            # Check if publication record exists
            existing_publication = session.query(Publication).filter_by(
                user_id=self.current_user_id,
                title=pub_item.get('title', '')
            ).first()
            
            if existing_publication:
                # Update existing publication
                existing_publication.publication_type = pub_item.get('publication_type', 'journal')
                existing_publication.journal_name = pub_item.get('journal_name', '')
                existing_publication.publication_date = pub_item.get('publication_date')
                existing_publication.doi = pub_item.get('doi', '')
                existing_publication.is_peer_reviewed = pub_item.get('is_peer_reviewed', True)
                existing_publication.updated_at = datetime.utcnow()
                
                publication = existing_publication
                self.sync_stats['updated_count'] += 1
            else:
                # Create new publication record
                publication = Publication(
                    user_id=self.current_user_id,
                    title=pub_item.get('title', ''),
                    publication_type=pub_item.get('publication_type', 'journal'),
                    journal_name=pub_item.get('journal_name', ''),
                    publication_date=pub_item.get('publication_date'),
                    doi=pub_item.get('doi', ''),
                    is_peer_reviewed=pub_item.get('is_peer_reviewed', True),
                    sort_order=len(session.query(Publication).filter_by(user_id=self.current_user_id).all())
                )
                session.add(publication)
                session.flush()
                session.refresh(publication)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1
            
            # Check if publication authors already exist for this publication
            existing_authors_count = session.query(PublicationAuthor).filter_by(
                publication_id=publication.id
            ).count()
            
            if existing_authors_count > 0:
                continue
            
            # Sync publication authors
            authors = pub_item.get('authors', [])
            for i, author in enumerate(authors):
                # Handle both string and dict format for authors
                if isinstance(author, str):
                    author_name = author
                    is_corresponding = False
                    affiliation = ''
                else:
                    author_name = author.get('name', '')
                    is_corresponding = author.get('is_corresponding', False)
                    affiliation = author.get('affiliation', '')
                
                publication_author = PublicationAuthor(
                    publication_id=publication.id,
                    author_name=author_name,
                    author_order=i,
                    is_corresponding=is_corresponding,
                    affiliation=affiliation
                )
                session.add(publication_author)
                self.sync_stats['created_count'] += 1
    
    def _sync_publication_authors(self, session: Session, publication: Publication, authors: List[str]) -> None:
        """Sync publication authors for a publication"""
        # Check if authors already exist to avoid duplicates
        try:
            existing_count = session.query(PublicationAuthor).filter(
                PublicationAuthor.publication_id == str(publication.id)
            ).count()
            if existing_count > 0:
                self.debug(f"Publication authors already exist for publication {publication.id}, skipping")
                return
        except Exception as e:
            self.warning(f"Error checking existing publication authors, proceeding: {e}")
        
        for i, author_name in enumerate(authors):
            if not author_name or not author_name.strip():
                continue
                
            # Create author record
            author = PublicationAuthor(
                publication_id=publication.id,
                author_name=author_name.strip(),
                author_order=i + 1,
                is_corresponding=False  # Could be enhanced to detect corresponding author
            )
            session.add(author)
    
    def _sync_research_projects(self, session: Session, research_data: List[Dict[str, Any]]) -> None:
        """Sync research projects data to database"""
        for research_item in research_data:
            # Check if research project record exists
            existing_research = session.query(ResearchProject).filter_by(
                user_id=self.current_user_id,
                title=research_item.get('title', research_item.get('institution', ''))
            ).first()
            
            if existing_research:
                # Update existing research project
                existing_research.start_date = self._parse_date(research_item.get('start_date'))
                existing_research.end_date = self._parse_date(research_item.get('end_date'))
                existing_research.is_ongoing = research_item.get('is_current', False)
                existing_research.location = research_item.get('location', '')
                existing_research.research_type = research_item.get('position', research_item.get('research_area', ''))
                existing_research.funding_source = research_item.get('funding_source', '')
                existing_research.updated_at = datetime.utcnow()
                
                research_project = existing_research
                self.sync_stats['updated_count'] += 1
            else:
                # Create new research project record
                research_project = ResearchProject(
                    user_id=self.current_user_id,
                    title=research_item.get('title', research_item.get('institution', 'Research Project')),
                    start_date=self._parse_date(research_item.get('start_date')),
                    end_date=self._parse_date(research_item.get('end_date')),
                    is_ongoing=research_item.get('is_current', False),
                    location=research_item.get('location', ''),
                    research_type=research_item.get('position', research_item.get('research_area', '')),
                    funding_source=research_item.get('funding_source', ''),
                    sort_order=len(session.query(ResearchProject).filter_by(user_id=self.current_user_id).all())
                )
                session.add(research_project)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(research_project)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1
            
            # Sync research project details if present
            details = research_item.get('details', [])
            if details:
                session.flush()
                session.refresh(research_project)
                # Now sync research project details
                self._sync_research_project_details(session, research_project, details)
    
    def _sync_research_project_details(self, session: Session, research_project: ResearchProject, details: List[str]) -> None:
        """Sync research project details to database"""
        
        # Check if details already exist
        existing_count = session.query(ResearchProjectDetail).filter(
            ResearchProjectDetail.research_project_id == research_project.id
        ).count()
        
        if existing_count > 0:
            return
        
        # Create research project details
        for i, detail_text in enumerate(details):
            if not detail_text or not detail_text.strip():
                continue
            
            try:
                research_project_detail = ResearchProjectDetail(
                    research_project_id=research_project.id,
                    detail_text=detail_text.strip(),
                    sort_order=i
                )
                session.add(research_project_detail)
                # Force individual insert to avoid insertmanyvalues bulk processing
                session.flush()
                self.sync_stats['created_count'] += 1
            except Exception as e:
                self.warning(f"Failed to create research project detail: {e}")
                continue
    
    def _sync_social_links(self, session: Session, personal_info: PersonalInfo, social_links_data: List[Dict[str, Any]]) -> None:
        """Sync social links data to database"""
        # Check if social links already exist for this personal info
        existing_links_count = session.query(SocialLink).filter_by(
            personal_info_id=personal_info.id
        ).count()
        
        if existing_links_count > 0:
            return
        
        # Create new social links
        for i, link_data in enumerate(social_links_data):
            social_link = SocialLink(
                personal_info_id=personal_info.id,
                platform=link_data.get('platform', ''),
                url=link_data.get('url', ''),
                display_name=link_data.get('display_name', ''),
                is_active=link_data.get('is_active', True),
                sort_order=i
            )
            session.add(social_link)
            self.sync_stats['created_count'] += 1

    def _sync_education_with_cleanup(self, session: Session, education_data: List[Dict[str, Any]]) -> None:
        """Sync education data with cleanup - replace all existing records"""
        try:
            # First, delete all existing education records for this user
            existing_educations = session.query(Education).filter_by(user_id=self.current_user_id).all()
            deleted_count = 0

            for education in existing_educations:
                # Delete related education details first using individual queries
                education_details = session.query(EducationDetail).filter(
                    EducationDetail.education_id == education.id
                ).all()
                for detail in education_details:
                    session.delete(detail)
                session.delete(education)
                deleted_count += 1

            if deleted_count > 0:
                session.flush()  # Flush deletions before creating new records
                self.debug(f"Cleaned up {deleted_count} existing education records")

            # Then, create all new education records from the file
            for i, edu_item in enumerate(education_data):
                education = Education(
                    user_id=self.current_user_id,
                    institution=edu_item.get('institution', ''),
                    degree=edu_item.get('degree', ''),
                    field_of_study=edu_item.get('field_of_study', ''),
                    start_date=self._parse_date(edu_item.get('start_date')),
                    end_date=self._parse_date(edu_item.get('end_date')),
                    is_current=edu_item.get('is_current', False),
                    gpa=edu_item.get('gpa'),
                    location=edu_item.get('location', ''),
                    institution_website=edu_item.get('institution_website', ''),
                    institution_logo_url=edu_item.get('institution_logo_url', ''),
                    sort_order=i
                )
                session.add(education)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(education)
                self.sync_stats['created_count'] += 1

                # Sync education details if present
                details = edu_item.get('details', [])
                if details:
                    self._sync_education_details(session, education, details)

        except Exception as e:
            raise DatabaseError(f"Failed to sync education with cleanup: {e}")

    def _sync_work_experience_with_cleanup(self, session: Session, experience_data: List[Dict[str, Any]]) -> None:
        """Sync work experience data with cleanup - replace all existing records"""
        try:
            # First, delete all existing work experience records for this user
            existing_experiences = session.query(WorkExperience).filter_by(user_id=self.current_user_id).all()
            deleted_count = 0

            for experience in existing_experiences:
                # Delete related work experience details first
                session.query(WorkExperienceDetail).filter(
                    WorkExperienceDetail.work_experience_id == experience.id
                ).delete()
                session.delete(experience)
                deleted_count += 1
            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing work experience records")

            # Then, create all new work experience records from the file
            for i, exp_item in enumerate(experience_data):
                work_experience = WorkExperience(
                    user_id=self.current_user_id,
                    company=exp_item.get('company', ''),
                    position=exp_item.get('position', ''),
                    start_date=self._parse_date(exp_item.get('start_date')),
                    end_date=self._parse_date(exp_item.get('end_date')),
                    is_current=exp_item.get('is_current', False),
                    location=exp_item.get('location', ''),
                    company_website=exp_item.get('company_website', ''),
                    company_logo_url=exp_item.get('company_logo_url', ''),
                    sort_order=i
                )
                session.add(work_experience)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(work_experience)
                self.sync_stats['created_count'] += 1

                # Sync work experience details if present
                details = exp_item.get('details', [])
                if details:
                    self._sync_work_experience_details(session, work_experience, details)

        except Exception as e:
            raise DatabaseError(f"Failed to sync work experience with cleanup: {e}")

    def _sync_awards_with_cleanup(self, session: Session, awards_data: List[Dict[str, Any]]) -> None:
        """Sync awards data with cleanup - replace all existing records"""
        try:
            # First, delete all existing awards for this user
            existing_awards = session.query(Award).filter_by(user_id=self.current_user_id).all()
            deleted_count = len(existing_awards)

            for award in existing_awards:
                session.delete(award)

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing award records")

            # Then, create all new award records from the file
            for i, award_item in enumerate(awards_data):
                award = Award(
                    user_id=self.current_user_id,
                    title=award_item.get('title', ''),
                    awarding_organization=award_item.get('awarding_organization', award_item.get('issuer', '')),
                    award_date=self._parse_date(award_item.get('award_date')),
                    description=award_item.get('description', ''),
                    sort_order=i
                )
                session.add(award)
                self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync awards with cleanup: {e}")

    def _sync_publications_with_cleanup(self, session: Session, publications_data: List[Dict[str, Any]]) -> None:
        """Sync publications data with cleanup - replace all existing records"""
        try:
            # Use raw SQL for more reliable deletion with cascading
            session.execute(text("DELETE FROM publication_authors WHERE publication_id IN (SELECT id FROM publications WHERE user_id = :user_id)"),
                          {"user_id": self.current_user_id})
            result = session.execute(text("DELETE FROM publications WHERE user_id = :user_id"),
                                   {"user_id": self.current_user_id})
            deleted_count = result.rowcount

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing publication records")

            # Then, create all new publication records from the file
            for i, pub_item in enumerate(publications_data):
                publication = Publication(
                    user_id=self.current_user_id,
                    title=pub_item.get('title', ''),
                    publication_type=pub_item.get('publication_type', 'journal'),
                    journal_name=pub_item.get('journal_name', ''),
                    publication_date=pub_item.get('publication_date'),
                    doi=pub_item.get('doi', ''),
                    is_peer_reviewed=pub_item.get('is_peer_reviewed', True),
                    sort_order=i
                )
                session.add(publication)
                session.flush()
                session.refresh(publication)
                self.sync_stats['created_count'] += 1

                # Sync publication authors
                authors = pub_item.get('authors', [])
                for j, author in enumerate(authors):
                    # Handle both string and dict format for authors
                    if isinstance(author, str):
                        author_name = author
                        is_corresponding = False
                        affiliation = ''
                    else:
                        author_name = author.get('name', '')
                        is_corresponding = author.get('is_corresponding', False)
                        affiliation = author.get('affiliation', '')

                    publication_author = PublicationAuthor(
                        publication_id=publication.id,
                        author_name=author_name,
                        author_order=j,
                        is_corresponding=is_corresponding,
                        affiliation=affiliation
                    )
                    session.add(publication_author)
                    self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync publications with cleanup: {e}")

    def _sync_research_projects_with_cleanup(self, session: Session, research_data: List[Dict[str, Any]]) -> None:
        """Sync research projects data with cleanup - replace all existing records"""
        try:
            # Use raw SQL for more reliable deletion with cascading
            session.execute(text("DELETE FROM research_project_details WHERE research_project_id IN (SELECT id FROM research_projects WHERE user_id = :user_id)"),
                          {"user_id": self.current_user_id})
            result = session.execute(text("DELETE FROM research_projects WHERE user_id = :user_id"),
                                   {"user_id": self.current_user_id})
            deleted_count = result.rowcount

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing research project records")

            # Then, create all new research project records from the file
            for i, research_item in enumerate(research_data):
                research_project = ResearchProject(
                    user_id=self.current_user_id,
                    title=research_item.get('title', research_item.get('institution', 'Research Project')),
                    start_date=self._parse_date(research_item.get('start_date')),
                    end_date=self._parse_date(research_item.get('end_date')),
                    is_ongoing=research_item.get('is_current', False),
                    location=research_item.get('location', ''),
                    research_type=research_item.get('position', research_item.get('research_area', '')),
                    funding_source=research_item.get('funding_source', ''),
                    sort_order=i
                )
                session.add(research_project)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(research_project)
                self.sync_stats['created_count'] += 1

                # Sync research project details if present
                details = research_item.get('details', [])
                if details:
                    self._sync_research_project_details(session, research_project, details)

        except Exception as e:
            raise DatabaseError(f"Failed to sync research projects with cleanup: {e}")

    def _sync_social_links_with_cleanup(self, session: Session, personal_info: PersonalInfo, social_links_data: List[Dict[str, Any]]) -> None:
        """Sync social links data with cleanup - replace all existing records"""
        try:
            # First, delete all existing social links for this personal info
            existing_links = session.query(SocialLink).filter_by(personal_info_id=personal_info.id).all()
            deleted_count = len(existing_links)

            for link in existing_links:
                session.delete(link)

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing social link records")

            # Then, create all new social link records from the file
            for i, link_data in enumerate(social_links_data):
                social_link = SocialLink(
                    personal_info_id=personal_info.id,
                    platform=link_data.get('platform', ''),
                    url=link_data.get('url', ''),
                    display_name=link_data.get('display_name', ''),
                    is_active=link_data.get('is_active', True),
                    sort_order=i
                )
                session.add(social_link)
                self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync social links with cleanup: {e}")
    

    
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
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = frontmatter.get('title', 'Untitled Idea')
                        slug = frontmatter.get('slug', self._generate_slug(title))
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
    
    def _sync_blog_tags(self, session: Session, blog_post: BlogPost, tags: List[str]) -> None:
        """Sync blog tags for a post"""
        # Clear existing tags
        session.query(BlogPostTag).filter_by(blog_post_id=blog_post.id).delete()
        
        for tag_name in tags:
            if not tag_name or not tag_name.strip():
                continue
                
            tag_name = tag_name.strip()
            generated_slug = self._generate_slug(tag_name)
            
            # Get or create tag - check both name and slug to avoid conflicts
            tag = session.query(BlogTag).filter_by(name=tag_name).first()
            if not tag:
                # Check if a tag with this slug already exists
                tag_by_slug = session.query(BlogTag).filter_by(slug=generated_slug).first()
                if tag_by_slug:
                    # Use existing tag with same slug
                    tag = tag_by_slug
                else:
                    # Create new tag
                    tag = BlogTag(
                        name=tag_name,
                        slug=generated_slug
                    )
                    session.add(tag)
                    session.flush()
            
            # Create association if not already exists
            existing_association = session.query(BlogPostTag).filter_by(
                blog_post_id=blog_post.id,
                blog_tag_id=tag.id
            ).first()
            
            if not existing_association:
                blog_post_tag = BlogPostTag(
                    blog_post_id=blog_post.id,
                    blog_tag_id=tag.id
                )
                session.add(blog_post_tag)
    
    def _sync_blog_categories(self, session: Session, blog_post: BlogPost, categories: List[str]) -> None:
        """Sync blog categories for a post"""
        if categories and categories[0]:
            category_name = categories[0].strip()  # Take first category
            generated_slug = self._generate_slug(category_name)
            
            # Get or create category - check both name and slug to avoid conflicts
            category = session.query(BlogCategory).filter_by(name=category_name).first()
            if not category:
                # Check if a category with this slug already exists
                category_by_slug = session.query(BlogCategory).filter_by(slug=generated_slug).first()
                if category_by_slug:
                    # Use existing category with same slug
                    category = category_by_slug
                else:
                    # Create new category
                    category = BlogCategory(
                        name=category_name,
                        slug=generated_slug
                    )
                    session.add(category)
                    session.flush()
            
            blog_post.category_id = category.id
    
    def _sync_project_technologies(self, session: Session, project: Project, technologies: List[str]) -> None:
        """Sync project technologies"""
        # Clear existing technologies
        session.query(ProjectTechnology).filter_by(project_id=project.id).delete()
        
        for i, tech_name in enumerate(technologies):
            if not tech_name or not tech_name.strip():
                continue
                
            tech = ProjectTechnology(
                project_id=project.id,
                technology_name=tech_name,
                sort_order=i
            )
            session.add(tech)
    
    def _sync_project_details(self, session: Session, project: Project, content: str, license_str: Optional[str] = None, license_text: Optional[str] = None, version_str: Optional[str] = None) -> None:
        """Sync project details from content, license, and version."""
        # Check if details exist
        details = session.query(ProjectDetail).filter_by(project_id=project.id).first()
        # Note: License text reading is handled by the project parser, not here
        if not details:
            details = ProjectDetail(
                project_id=project.id,
                detailed_description=content or None,
                license=license_str,
                license_text=license_text,
                version=version_str
            )
            session.add(details)
        else:
            if content:
                details.detailed_description = content
            if license_str:
                details.license = license_str
            if license_text:
                details.license_text = license_text
            if version_str:
                details.version = version_str
            details.updated_at = datetime.utcnow()

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
    
    def _sync_blog_translations(self, session: Session, blog_post: BlogPost, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
        """Sync blog post translations for multi-language support"""
        try:
            # Check if this content has language information
            frontmatter = content_data.get('frontmatter', content_data)
            language = frontmatter.get('language', 'en')
            
            # If this is non-English content, handle it as a translation
            if language != 'en':
                # Import models
                from ..models.blog import BlogPostTranslation
                
                # Extract translation data
                title = frontmatter.get('title', '')
                excerpt = frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', '')))
                content = content_data.get('content', '')
                
                if not title or not content:
                    return
                
                # Check if translation already exists
                existing_translation = session.query(BlogPostTranslation).filter_by(
                    blog_post_id=blog_post.id,
                    language_code=language
                ).first()
                
                if existing_translation:
                    # Update existing translation
                    existing_translation.title = title
                    existing_translation.excerpt = excerpt
                    existing_translation.content = content
                    self.debug(f"Updated {language} translation for blog post: {blog_post.slug}")
                else:
                    # Create new translation
                    translation = BlogPostTranslation(
                        blog_post_id=blog_post.id,
                        language_code=language,
                        title=title,
                        excerpt=excerpt,
                        content=content
                    )
                    session.add(translation)
                    self.debug(f"Created {language} translation for blog post: {blog_post.slug}")
                    
        except Exception as e:
            self.warning(f"Failed to sync translations for blog post {blog_post.slug}: {e}")

    def _sync_blog_translation_only(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
        """Sync only translation for a blog post (find corresponding English post)"""
        try:
            # Import models
            from ..models.blog import BlogPostTranslation
            
            frontmatter = content_data.get('frontmatter', content_data)
            language = frontmatter.get('language', 'en')
            
            if language == 'en':
                return  # This should not happen, but safety check
            
            item_name = item.get('name', '')
            if language in item_name:                
                # Try to find English post by matching folder pattern
                content_path = item.get('path', '')
                if content_path:
                    # Extract folder path and find English file
                    from pathlib import Path
                    path_obj = Path(content_path)
                    folder_path = path_obj.parent
                    english_file = folder_path / 'en.md'
                    
                    if english_file.exists():
                        # Read English file to get its title for matching
                        import frontmatter as fm
                        with open(english_file, 'r', encoding='utf-8') as f:
                            english_post = fm.load(f)
                            english_title = english_post.metadata.get('title', '')
                            english_slug = english_post.metadata.get('slug', self._generate_slug(str(english_title)))
                            
                            # Find the English blog post
                            english_blog_post = session.query(BlogPost).filter_by(slug=english_slug).first()
                            if not english_blog_post:
                                # Try to find by title
                                english_blog_post = session.query(BlogPost).filter_by(title=english_title).first()
                            
                            if english_blog_post:
                                # Create or update translation
                                title = frontmatter.get('title', '')
                                excerpt = frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', '')))
                                content = content_data.get('content', '')
                                
                                existing_translation = session.query(BlogPostTranslation).filter_by(
                                    blog_post_id=english_blog_post.id,
                                    language_code=language
                                ).first()
                                
                                if existing_translation:
                                    # Update existing translation
                                    existing_translation.title = title
                                    existing_translation.excerpt = excerpt
                                    existing_translation.content = content
                                    self.debug(f"Updated {language} translation for blog post: {english_blog_post.slug}")
                                else:
                                    # Create new translation
                                    translation = BlogPostTranslation(
                                        blog_post_id=english_blog_post.id,
                                        language_code=language,
                                        title=title,
                                        excerpt=excerpt,
                                        content=content
                                    )
                                    session.add(translation)
                                    self.debug(f"Created {language} translation for blog post: {english_blog_post.slug}")
                                    
                                session.commit()
                                return
                
                self.warning(f"Could not find corresponding English blog post for {language} translation: {item_name}")
            
        except Exception as e:
            self.warning(f"Failed to sync blog translation {item.get('name', '')}: {e}")

    def _sync_episode(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync episode content to database as specialized blog posts with series support"""
        try:
            # Extract episode data - episodes use parsed main_entity data
            main_entity = content_data.get('main_entity', {})
            frontmatter = content_data.get('frontmatter', {})
            content = main_entity.get('content', content_data.get('content', ''))

            # Episode-specific fields from parsed main_entity
            title = main_entity.get('title', 'Untitled Episode')
            slug = main_entity.get('slug', self._generate_slug(title))
            series_name = main_entity.get('series_name', '')
            episode_name = main_entity.get('episode_name', '')
            episode_number = main_entity.get('episode_number', 0)

            # Determine status
            status = self._determine_blog_status(frontmatter, content_data)

            # Check if episode exists
            existing_post = session.query(BlogPost).filter_by(slug=slug).first()

            if existing_post:
                # Update existing episode
                from ..models.blog import BlogStatus, BlogContentType
                existing_post.title = title
                existing_post.content = content
                existing_post.excerpt = main_entity.get('description', frontmatter.get('description', frontmatter.get('summary', '')))
                existing_post.is_featured = main_entity.get('is_featured', frontmatter.get('featured', False))
                existing_post.content_type = BlogContentType.EPISODE
                existing_post.status = BlogStatus(status.lower())
                existing_post.updated_at = datetime.utcnow()

                # Handle view and like counts
                existing_post.view_count = main_entity.get('view_count', frontmatter.get('views', existing_post.view_count))
                existing_post.like_count = main_entity.get('like_count', frontmatter.get('likes', existing_post.like_count))

                published_date = main_entity.get('published_date') or frontmatter.get('published_date')
                if published_date:
                    existing_post.published_at = self._parse_datetime(published_date)

                blog_post = existing_post
                self.sync_stats['updated_count'] += 1
            else:
                # Create new episode
                from ..models.blog import BlogStatus, BlogContentType
                assert self.current_user_id is not None
                published_date = main_entity.get('published_date') or frontmatter.get('published_date')
                blog_post = BlogPost(
                    user_id=self.current_user_id,
                    title=title,
                    slug=slug,
                    content=content,
                    excerpt=main_entity.get('description', frontmatter.get('description', frontmatter.get('summary', ''))),
                    is_featured=main_entity.get('is_featured', frontmatter.get('featured', False)),
                    content_type=BlogContentType.EPISODE,
                    status=BlogStatus(status.lower()),
                    view_count=main_entity.get('view_count', frontmatter.get('views', 0)),
                    like_count=main_entity.get('like_count', frontmatter.get('likes', 0)),
                    published_at=self._parse_datetime(published_date or datetime.utcnow())
                )
                session.add(blog_post)
                session.flush()  # Get the ID
                self.sync_stats['created_count'] += 1

            # Handle series information
            if series_name:
                self._sync_episode_series(session, blog_post, series_name, episode_number, frontmatter)

            # Handle tags and categories
            categories = content_data.get('categories', [])
            if not categories:
                categories = frontmatter.get('categories', [])
            if isinstance(categories, str):
                categories = [categories]

            # Add series as category
            if series_name and series_name not in categories:
                categories.append(series_name)

            if categories:
                self._sync_blog_categories(session, blog_post, categories)

            # Handle tags
            tags = content_data.get('tags', [])
            if not tags:
                tags = frontmatter.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]

            # Add episode-specific tags
            if episode_name:
                tags.append(f"episode-{episode_name}")
            if series_name:
                tags.append(f"series-{series_name}")

            if tags:
                self._sync_blog_tags(session, blog_post, tags)

            self.debug(f"✅ Synced episode: {title}")

        except Exception as e:
            self.warning(f"Failed to sync episode {item.get('name', '')}: {e}")

    def _sync_episode_series(self, session: Session, blog_post: BlogPost, series_name: str, episode_number: int, frontmatter: Dict[str, Any]) -> None:
        """Handle series information for episodes"""
        try:
            from ..models.blog import BlogSeries, BlogSeriesTranslation

            # Find or create series
            existing_series = session.query(BlogSeries).filter_by(slug=self._generate_slug(series_name)).first()

            if not existing_series:
                # Create new series
                series = BlogSeries(
                    title=series_name.replace('-', ' ').title(),
                    slug=self._generate_slug(series_name),
                    description=frontmatter.get('series_description', f"Episodes from the {series_name} series"),
                    status="active"
                )
                session.add(series)
                session.flush()

                # Create English translation for series
                series_translation = BlogSeriesTranslation(
                    blog_series_id=series.id,
                    language_code='en',
                    title=series.title,
                    description=series.description
                )
                session.add(series_translation)
            else:
                series = existing_series

            # Associate blog post with series
            blog_post.series_id = series.id
            blog_post.episode_number = episode_number

            # Update series episode count
            episode_count = session.query(BlogPost).filter_by(series_id=series.id).count()
            series.episode_count = episode_count

        except Exception as e:
            self.warning(f"Failed to sync episode series {series_name}: {e}")

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
                frontmatter = content_data.get('frontmatter', content_data)
                title = frontmatter.get('title', 'Untitled Idea')
                slug = frontmatter.get('slug', self._generate_slug(title))
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
                        frontmatter = content_data.get('frontmatter', content_data)
                        title = frontmatter.get('title', 'Untitled Idea')
                        slug = frontmatter.get('slug', self._generate_slug(title))
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