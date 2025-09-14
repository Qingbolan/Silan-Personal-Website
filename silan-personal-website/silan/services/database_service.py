"""Database service for handling database operations"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from ..core.interfaces import IService
from ..core.exceptions import DatabaseError
from ..models import Base
from ..utils import ModernLogger


class DatabaseService(IService):
    """Service for database operations with proper connection management"""
    
    def __init__(self, database_config: Union[str, Dict[str, Any]], logger: Optional[ModernLogger] = None):
        self.logger = logger or ModernLogger(name="database_service")
        self.database_config = database_config
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._connection_info: Optional[Dict[str, Any]] = None
    
    def initialize(self) -> bool:
        """Initialize database connection and session factory"""
        try:
            # Create database engine
            connection_string = self._build_connection_string()
            self.engine = create_engine(
                connection_string,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True  # Verify connections before use
            )
            
            # Test connection
            with self.engine.connect() as conn:
                self.logger.debug("Database connection test successful")
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Store connection info for display
            self._connection_info = self._extract_connection_info()
            
            self.logger.info(f"✅ Database service initialized: {self._connection_info['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database service: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up database resources"""
        try:
            if self.engine:
                self.engine.dispose()
                self.logger.debug("Database engine disposed")
        except Exception as e:
            self.logger.error(f"Error during database cleanup: {e}")
    
    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string from config"""
        if isinstance(self.database_config, str):
            return self.database_config
        
        config = self.database_config
        db_type = config['type']
        
        if db_type == 'sqlite':
            db_path = config['path']
            # Ensure directory exists for SQLite database
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"
        
        elif db_type == 'mysql':
            host = config['host']
            port = config.get('port', 3306)
            user = config['user']
            password = config.get('password', '')
            database = config['database']
            
            # Add charset and other MySQL-specific options
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
    
    def _extract_connection_info(self) -> Dict[str, Any]:
        """Extract connection information for display"""
        if isinstance(self.database_config, str):
            return {'type': 'custom', 'connection_string': self.database_config}
        
        config = self.database_config
        info = {'type': config['type']}
        
        if config['type'] == 'sqlite':
            info['path'] = config['path']
        else:
            info['host'] = config['host']
            info['port'] = config.get('port')
            info['database'] = config['database']
            info['user'] = config['user']
        
        return info
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for display"""
        return self._connection_info or {}
    
    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            if not self.engine:
                raise DatabaseError("Database not initialized")
            
            Base.metadata.create_all(self.engine)
            self.logger.info("✅ Database tables created/verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")
            return False
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.session_factory:
            raise DatabaseError("Database service not initialized")
        return self.session_factory()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.engine:
                return False
            
            with self.engine.connect() as conn:
                # Simple query to test connection
                result = conn.execute(select(1))
                result.fetchone()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_all_content_hashes(self) -> Dict[str, str]:
        """Get all content hashes from database for comparison"""
        try:
            # This is a placeholder - implement based on your specific models
            # In a real implementation, you'd query your content tables and return
            # a mapping of content_id -> content_hash
            
            hashes = {}
            
            # Example implementation (adjust based on your models):
            # with self.get_session() as session:
            #     blog_posts = session.query(BlogPost).all()
            #     for post in blog_posts:
            #         hashes[f"blog_{post.slug}"] = post.content_hash
            #     
            #     projects = session.query(Project).all()
            #     for project in projects:
            #         hashes[f"project_{project.slug}"] = project.content_hash
            
            return hashes
            
        except Exception as e:
            self.logger.error(f"Failed to get content hashes: {e}")
            return {}
    
    def sync_content_item(self, content_item: Dict[str, Any]) -> bool:
        """Sync a single content item to database"""
        try:
            # This is a placeholder - implement based on your specific models
            # In a real implementation, you'd:
            # 1. Parse the content_item 
            # 2. Create or update the appropriate model instances
            # 3. Save to database
            
            content_type = content_item.get('type')
            content_data = content_item.get('data')
            
            self.logger.debug(f"Syncing {content_type} content: {content_item.get('path')}")
            
            # Example implementation:
            # if content_type == 'blog':
            #     self._sync_blog_post(content_data)
            # elif content_type == 'project':
            #     self._sync_project(content_data)
            # elif content_type == 'idea':
            #     self._sync_idea(content_data)
            # else:
            #     raise DatabaseError(f"Unknown content type: {content_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync content item: {e}")
            return False
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        try:
            # This would query your database to get current counts
            # Example implementation:
            
            stats = {
                'total_blog_posts': 0,
                'total_projects': 0,
                'total_ideas': 0,
                'total_updates': 0,
                'last_sync': 'Never'
            }
            
            # with self.get_session() as session:
            #     stats['total_blog_posts'] = session.query(BlogPost).count()
            #     stats['total_projects'] = session.query(Project).count()
            #     stats['total_ideas'] = session.query(Idea).count()
            #     stats['total_updates'] = session.query(RecentUpdate).count()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get sync statistics: {e}")
            return {}