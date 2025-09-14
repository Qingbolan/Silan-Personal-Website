"""Database synchronization business logic implementation"""

import json
from pathlib import Path
from typing import Dict, Any, Union, List, Optional, cast
from datetime import datetime, date
from rich.progress import TaskID
from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker, Session

from ..core.exceptions import DatabaseError, ValidationError
from ..models import (
    Base, User, BlogPost, BlogTag, BlogPostTag, BlogPostTranslation,
    BlogCategory, BlogSeries, BlogSeriesTranslation, Project, ProjectTechnology,
    ProjectDetail, Idea, RecentUpdate, PersonalInfo,
    Education, EducationDetail, WorkExperience, WorkExperienceDetail, Award, Publication, PublicationAuthor,
    ResearchProject, ResearchProjectDetail, SocialLink
)
from ..parsers import ParserFactory
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
            
            # Log completion
            self.sync_complete(
                self.sync_stats['success_count'],
                self.sync_stats['error_count']
            )
            
            # Save sync summary
            if not self.dry_run:
                self.save_sync_summary()
            
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
                pool_pre_ping=True,
                # Disable insertmanyvalues optimization to avoid sentinel mismatch on SQLite
                **({} if not connection_string.startswith("sqlite") else {"connect_args": {"check_same_thread": False}})
            )
            # ------------------------------------------------------------------
            # SQLAlchemy 2.0 enables the insertmanyvalues optimization by default
            # which relies on RETURNING clauses to bulk-insert several rows at
            # once.  When we work with CHAR(36) UUID primary keys on SQLite this
            # optimisation can raise the following runtime error during a flush
            # / commit (observed when syncing experience details):
            #
            #    Can't match sentinel values in result set to parameter sets;
            #    key 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' was not found
            #
            # The issue is tracked upstream in SQLAlchemy (see GH-9618) and will
            # eventually be fixed, but  the safest workaround for now is to
            # disable insertmanyvalues for SQLite engines.  This turns the bulk
            # insert back into individual INSERT statements and removes the
            # sentinel mapping step that triggers the crash.
            # ------------------------------------------------------------------
            
            # Test connection
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Apply execution options to disable insertmanyvalues for SQLite
            if connection_string.startswith("sqlite"):
                self.engine = self.engine.execution_options(insertmanyvalues=False)
            
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
        """Sync a single content item to database"""
        try:
            if not self.session_factory:
                raise DatabaseError("Database session factory not initialized")
            
            with self.session_factory() as session:
                # Ensure user exists
                if not self.current_user_id:
                    user = self._get_or_create_user(session)
                    self.current_user_id = user.id
                
                if not self.current_user_id:
                    raise DatabaseError("Failed to get or create user")
                
                content_type = item['type']
                content_data = item['data']
                
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
                        self._sync_blog_post(session, content_data, item)
                elif content_type == 'projects':
                    self._sync_project(session, content_data, item)
                elif content_type == 'ideas':
                    self._sync_idea(session, content_data, item)
                elif content_type == 'updates':
                    self._sync_update(session, content_data, item)
                elif content_type == 'resume':
                    self._sync_resume(session, content_data, item)
                else:
                    self.warning(f"Unknown content type: {content_type}")
                    return
                
                session.commit()
                self.sync_stats['created_count'] += 1
                
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Failed to sync content item: {e}")
    
    def _sync_blog_post(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
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
                # Update existing post
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
                
                blog_post = existing_post
                self.sync_stats['updated_count'] += 1
            else:
                # Create new post
                from ..models.blog import BlogStatus, BlogContentType
                assert self.current_user_id is not None
                blog_post = BlogPost(
                    user_id=self.current_user_id,
                    title=title,
                    slug=slug,
                    content=content,
                    excerpt=frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', ''))),
                    is_featured=frontmatter.get('featured', False),
                    content_type=BlogContentType(content_type.lower()),
                    status=BlogStatus(status.lower()),
                    view_count=frontmatter.get('views', 0),
                    like_count=frontmatter.get('likes', 0),
                    published_at=self._parse_datetime(frontmatter.get('date', datetime.utcnow()))
                )
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
    
    def _sync_project(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
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
                
                project = existing_project
                self.sync_stats['updated_count'] += 1
            else:
                # Create new project
                assert self.current_user_id is not None
                project = Project(
                    user_id=self.current_user_id,
                    title=title,
                    slug=slug,
                    description=description,
                    github_url=github_url,
                    demo_url=demo_url,
                    is_featured=is_featured,
                    is_public=True,  # Set as public so it shows in API
                    start_date=self._parse_date(start_date),
                    end_date=self._parse_date(end_date)
                )
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
            
            # Handle project details
            if content:
                self._sync_project_details(session, project, content)
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync project: {e}")
    
    def _sync_idea(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
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
                
                idea = existing_idea
                self.sync_stats['updated_count'] += 1
            else:
                # Create new idea
                assert self.current_user_id is not None
                idea = Idea(
                    user_id=self.current_user_id,
                    title=title,
                    slug=slug,
                    abstract=frontmatter.get('abstract', frontmatter.get('description', '')),
                    motivation=content if content else None,
                    is_public=True  # Set as public so it shows in API
                )
                session.add(idea)
                session.flush()
                self.sync_stats['created_count'] += 1
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync idea: {e}")
    
    def _sync_update(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
        """Sync update to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')
            
            title = frontmatter.get('title', 'Untitled Update')
            update_date = self._parse_date(frontmatter.get('date', datetime.utcnow().date()))
            
            # Check if update exists (by title and date)
            existing_update = session.query(RecentUpdate).filter(
                and_(
                    RecentUpdate.title == title,
                    RecentUpdate.date == update_date
                )
            ).first()
            
            if existing_update:
                # Update existing update
                existing_update.description = content or frontmatter.get('description', '')
                existing_update.updated_at = datetime.utcnow()
                
                update = existing_update
                self.sync_stats['updated_count'] += 1
            else:
                # Create new update
                assert self.current_user_id is not None
                update = RecentUpdate(
                    user_id=self.current_user_id,
                    title=title,
                    description=content or frontmatter.get('description', ''),
                    date=update_date
                )
                session.add(update)
                session.flush()
                self.sync_stats['created_count'] += 1
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync update: {e}")
    
    def _sync_resume(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
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
            
            # Resume content is typically stored in personal_info table
            # Check if personal info exists
            existing_info = session.query(PersonalInfo).first()
            
            if existing_info:
                # Update existing personal info
                existing_info.full_name = frontmatter.get('name', frontmatter.get('full_name', ''))
                existing_info.title = frontmatter.get('title', frontmatter.get('current_position', ''))
                existing_info.current_status = frontmatter.get('bio', frontmatter.get('summary', ''))
                existing_info.location = frontmatter.get('location', '')
                existing_info.email = frontmatter.get('email', '')
                existing_info.phone = frontmatter.get('phone', '')
                existing_info.website = frontmatter.get('website', '')
                existing_info.avatar_url = frontmatter.get('profile_image', frontmatter.get('avatar_url', ''))
                existing_info.updated_at = datetime.utcnow()
                
                personal_info = existing_info
                self.sync_stats['updated_count'] += 1
            else:
                # Create new personal info
                assert self.current_user_id is not None
                personal_info = PersonalInfo(
                    user_id=self.current_user_id,
                    full_name=frontmatter.get('name', frontmatter.get('full_name', 'Unknown')),
                    title=frontmatter.get('title', frontmatter.get('current_position', 'Professional')),
                    current_status=frontmatter.get('bio', frontmatter.get('summary', '')),
                    location=frontmatter.get('location', ''),
                    email=frontmatter.get('email', ''),
                    phone=frontmatter.get('phone', ''),
                    website=frontmatter.get('website', ''),
                    avatar_url=frontmatter.get('profile_image', frontmatter.get('avatar_url', '')),
                    is_primary=True
                )
                session.add(personal_info)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(personal_info)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1
            
            # Sync education data if available
            try:
                education_data = content_data.get('education', [])
                if education_data:
                    self._sync_education(session, education_data)
            except Exception as e:
                self.error(f"Education sync failed: {e}")
                raise
            
            # Sync work experience data if available
            try:
                experience_data = content_data.get('experience', [])
                if experience_data:
                    self._sync_work_experience(session, experience_data)
            except Exception as e:
                self.error(f"Experience sync failed: {e}")
                raise
            
            # Sync awards data if available
            try:
                awards_data = content_data.get('awards', [])
                if awards_data:
                    self._sync_awards(session, awards_data)
            except Exception as e:
                self.error(f"Awards sync failed: {e}")
                raise
            
            # Sync publications data if available
            try:
                publications_data = content_data.get('publications', [])
                if publications_data:
                    self._sync_publications(session, publications_data)
            except Exception as e:
                self.error(f"Publications sync failed: {e}")
                raise
            
            # Sync research projects data if available
            try:
                research_data = content_data.get('research', [])
                if research_data:
                    self._sync_research_projects(session, research_data)
            except Exception as e:
                self.error(f"Research projects sync failed: {e}")
                raise
            
            # Sync social links data if available
            try:
                social_links_data = content_data.get('social_links', [])
                if social_links_data:
                    self._sync_social_links(session, personal_info, social_links_data)
            except Exception as e:
                self.error(f"Social links sync failed: {e}")
                raise
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync resume: {e}")
    
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
    

    
    def _simulate_sync_item(self, item: Dict[str, Any]) -> None:
        """Simulate syncing an item (dry run)"""
        self.debug(f"[DRY RUN] Would sync {item['type']}: {item['name']}")
    
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
    
    def _sync_project_details(self, session: Session, project: Project, content: str) -> None:
        """Sync project details from content"""
        # Check if details exist
        details = session.query(ProjectDetail).filter_by(project_id=project.id).first()
        if not details:
            details = ProjectDetail(
                project_id=project.id,
                detailed_description=content
            )
            session.add(details)
        else:
            details.detailed_description = content
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
            
            summary_file = self.config_manager.project_dir / '.silan' / 'last_sync.json'
            with open(summary_file, 'w') as f:
                json.dump(sync_summary, f, indent=2)
            
            self.debug(f"Sync summary saved to {summary_file}")
            
        except Exception as e:
            self.error(f"Failed to save sync summary: {e}")
    
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
            
            # Extract the base name to find the corresponding English post
            # Example: "vlog.ai-coding-tutorial-zh" -> "vlog.ai-coding-tutorial-en"
            item_name = item.get('name', '')
            if language in item_name:
                # Remove language suffix and find English version
                base_name = item_name.replace(f'-{language}', '-en')
                
                # Try to find the English blog post by matching name pattern
                # We need to find a blog post that was created from the English version
                # Since we don't have direct slug mapping, we'll try to match by similar titles/content
                
                # Get base title by removing language-specific parts
                base_title = frontmatter.get('title', '').replace('Silan 个人网站：实时演示与教程', 'Silan Personal Website: Live Usage Demo and Tutorial')
                
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