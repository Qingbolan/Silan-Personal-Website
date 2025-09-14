"""Status logic for comprehensive project status display"""

import json
from pathlib import Path
from typing import Dict

from ..utils import ModernLogger, ConfigManager
from .content_logic import ContentLogic


class StatusLogic(ModernLogger):
    """Logic for displaying comprehensive project status"""
    
    def __init__(self):
        super().__init__(name="status_logic", level="info")
        self.project_dir = Path.cwd()
        self.config_dir = self.project_dir / ".silan"
        
        # Initialize services
        self.config_manager = ConfigManager(self.project_dir)
        self.content_logic = ContentLogic()
    
    def show_project_status(self) -> None:
        """Show project overview and configuration"""
        self.banner("PROJECT STATUS", "Silan Database Tools", "Current Project Overview")
        
        # Project information
        project_info = {
            "Project Directory": str(self.project_dir),
            "Configuration Directory": str(self.config_dir),
            "Config Dir Exists": "✅" if self.config_dir.exists() else "❌",
            "Git Repository": "✅" if (self.project_dir / ".git").exists() else "❌"
        }
        
        self.info("📂 Project Information:")
        for key, value in project_info.items():
            self.info(f"  {key}: {value}")
        
        # Check for important files
        important_files = [
            "README.md",
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "go.mod"
        ]
        
        existing_files = []
        for file_name in important_files:
            if (self.project_dir / file_name).exists():
                existing_files.append(file_name)
        
        if existing_files:
            self.info(f"📄 Important Files Found: {', '.join(existing_files)}")
            
    def show_database_status(self) -> None:
        """Show database configuration and connection status"""
        self.stage("DATABASE STATUS")
        
        # Check for cached database config
        cache_file = self.config_dir / ".silan_db_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_config = json.load(f)
                
                self.info("💾 Cached Database Configuration:")
                self.info(f"  Database Type: {cached_config.get('type', 'Unknown')}")
                
                if cached_config.get('type') == 'sqlite':
                    db_path = cached_config.get('path', 'portfolio.db')
                    self.info(f"  Database Path: {db_path}")
                    
                    # Check if SQLite file exists
                    if Path(db_path).exists():
                        file_size = Path(db_path).stat().st_size
                        self.info(f"  Database Size: {file_size:,} bytes")
                        self.info("  Status: ✅ Database file exists")
                    else:
                        self.warning("  Status: ❌ Database file not found")
                        
                else:
                    self.info(f"  Host: {cached_config.get('host', 'Unknown')}")
                    self.info(f"  Port: {cached_config.get('port', 'Unknown')}")
                    self.info(f"  Database: {cached_config.get('database', 'Unknown')}")
                    self.info(f"  User: {cached_config.get('user', 'Unknown')}")
                    
                    # Try to test connection (basic ping)
                    try:
                        from .database_sync_logic import DatabaseSyncLogic
                        sync_logic = DatabaseSyncLogic(cached_config, dry_run=True)
                        if sync_logic._initialize_database():
                            sync_logic._cleanup_database()
                            self.info("  Status: ✅ Database connection successful")
                        else:
                            self.warning("  Status: ❌ Database connection failed")
                    except Exception as e:
                        self.error(f"  Status: ❌ Connection test failed: {e}")
                        
            except Exception as e:
                self.error(f"Failed to read cached database config: {e}")
        else:
            self.warning("❌ No cached database configuration found")
            self.info("   Run 'silan db-config interactive' to set up database")
        
        # Check for last sync info
        last_sync_file = self.config_dir / ".silan_last_sync.json"
        if last_sync_file.exists():
            try:
                with open(last_sync_file, 'r') as f:
                    last_sync = json.load(f)
                
                self.info("🔄 Last Sync Information:")
                self.info(f"  Date: {last_sync.get('timestamp', 'Unknown')}")
                self.info(f"  Status: {last_sync.get('status', 'Unknown')}")
                self.info(f"  Items Synced: {last_sync.get('items_synced', 0)}")
                
                if last_sync.get('errors'):
                    self.warning(f"  Errors: {len(last_sync['errors'])}")
                    
            except Exception as e:
                self.error(f"Failed to read last sync info: {e}")
        else:
            self.info("📅 No previous sync found")
            
    def show_backend_status(self) -> None:
        """Show backend server status"""
        self.stage("BACKEND STATUS")
        
        try:
            # Check if backend process is running
            pid_file = self.config_dir / "backend.pid"
            if pid_file.exists():
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    import psutil
                    if psutil.pid_exists(pid):
                        self.info("🚀 Backend Server Status: ✅ Running")
                        self.info(f"  PID: {pid}")
                        self.info(f"  URL: http://localhost:8888")
                    else:
                        self.warning("🚀 Backend Server Status: ❌ Not Running")
                        self.info("   Run 'silan backend start' to start the server")
                except Exception:
                    self.warning("🚀 Backend Server Status: ❌ Not Running")
                    self.info("   Run 'silan backend start' to start the server")
            else:
                self.warning("🚀 Backend Server Status: ❌ Not Running")
                self.info("   Run 'silan backend start' to start the server")
            
            # Check if binary exists
            binary_path = self.config_dir / "backend"
            if binary_path.exists():
                self.info(f"📦 Backend Binary: ✅ Found at {binary_path}")
            else:
                self.warning("📦 Backend Binary: ❌ Not found")
                self.info("   Run 'silan backend install' to build the binary")
                
        except Exception as e:
            self.error(f"Failed to check backend status: {e}")
            
    def show_content_summary(self) -> None:
        """Show content files summary"""
        self.stage("CONTENT SUMMARY")
        
        try:
            # Look for content directories
            content_dirs = ['content', 'docs', 'posts', 'projects', 'blog']
            found_dirs = []
            
            for dir_name in content_dirs:
                dir_path = self.project_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    found_dirs.append(dir_name)
            
            if found_dirs:
                self.info(f"📁 Content Directories Found: {', '.join(found_dirs)}")
                
                # Count markdown files
                total_md_files = 0
                for dir_name in found_dirs:
                    dir_path = self.project_dir / dir_name
                    md_files = list(dir_path.rglob('*.md'))
                    total_md_files += len(md_files)
                    self.info(f"  {dir_name}/: {len(md_files)} markdown files")
                
                self.info(f"📄 Total Markdown Files: {total_md_files}")
                
                # Analyze content by parser type
                if total_md_files > 0:
                    self.info("📊 Content Analysis:")
                    content_stats = self._analyze_content_files(found_dirs)
                    
                    for content_type, count in content_stats.items():
                        self.info(f"  {content_type.title()}: {count} files")
                        
            else:
                self.warning("📁 No content directories found")
                self.info("   Create a 'content' directory and add markdown files")
                
        except Exception as e:
            self.error(f"Failed to analyze content: {e}")
            
    def _analyze_content_files(self, content_dirs: list) -> Dict[str, int]:
        """Analyze content files by type"""
        stats = {}
        
        try:
            for dir_name in content_dirs:
                dir_path = self.project_dir / dir_name
                
                # Use content logic to analyze files
                content_summary = self.content_logic.get_content_summary()
                return content_summary.get('content_types', {})
                    
        except Exception as e:
            self.error(f"Error analyzing content files: {e}")
            return {"unknown": 0}
        
        return stats
    
    def show_quick_actions(self) -> None:
        """Show suggested next actions"""
        self.stage("QUICK ACTIONS")
        
        actions = []
        
        # Check if database is configured
        cache_file = self.config_dir / ".silan_db_cache.json"
        if not cache_file.exists():
            actions.append("🔧 Configure database: silan db-config interactive")
        
        # Check if backend is running
        try:
            pid_file = self.config_dir / "backend.pid"
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                import psutil
                if not psutil.pid_exists(pid):
                    actions.append("🚀 Start backend server: silan backend start")
            else:
                actions.append("🚀 Start backend server: silan backend start")
        except:
            actions.append("🚀 Start backend server: silan backend start")
        
        # Check if content needs syncing
        if cache_file.exists():
            actions.append("🔄 Sync content to database: silan db-sync")
        
        # Check if there are content files
        content_dir = self.project_dir / "content"
        if content_dir.exists():
            actions.append("📊 View detailed status: silan status")
        else:
            actions.append("📁 Initialize project: silan init my-project")
        
        if actions:
            self.info("💡 Suggested Actions:")
            for action in actions:
                self.info(f"  {action}")
        else:
            self.info("✅ Everything looks good! Your project is ready to go.")