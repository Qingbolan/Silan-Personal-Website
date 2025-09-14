"""Help logic for displaying comprehensive help information"""
from ..utils import ModernLogger


class HelpLogic(ModernLogger):
    """Logic for displaying help information"""
    
    def __init__(self):
        super().__init__(name="help_logic", level="info")        
        # Help content structure
        self.help_topics = {
            "general": {
                "title": "General Help",
                "description": "Overview of Silan Database Tools",
                "content": self._get_general_help_content()
            },
            "init": {
                "title": "Project Initialization",
                "description": "Initialize new projects with content templates",
                "content": self._get_init_help_content()
            },
            "db-sync": {
                "title": "Database Synchronization",
                "description": "Sync markdown content to databases",
                "content": self._get_db_sync_help_content()
            },
            "db-config": {
                "title": "Database Configuration",
                "description": "Manage database connection settings",
                "content": self._get_db_config_help_content()
            },
            "backend": {
                "title": "Backend Server Management",
                "description": "Manage the Go backend server",
                "content": self._get_backend_help_content()
            },
            "status": {
                "title": "Project Status",
                "description": "View project and system status",
                "content": self._get_status_help_content()
            },
            "workflows": {
                "title": "Common Workflows",
                "description": "Step-by-step guides for common tasks",
                "content": self._get_workflows_help_content()
            },
            "troubleshooting": {
                "title": "Troubleshooting",
                "description": "Solutions for common issues",
                "content": self._get_troubleshooting_help_content()
            }
        }
    
    def show_general_help(self) -> bool:
        """Show general help overview"""
        self.banner("SILAN HELP", "Silan Database Tools", "Command Reference & Documentation")
        
        self.info("🎯 OVERVIEW")
        self.info("Silan Database Tools helps you sync markdown content to databases")
        self.info("and serve it through a Go backend API with a clean web interface.")
        
        self.info("🚀 QUICK START")
        self.info("1. Initialize a new project:    silan init my-project")
        self.info("2. Configure your database:     silan db-config interactive")
        self.info("3. Sync your content:          silan db-sync")
        self.info("4. Start the backend server:   silan backend start")
        
        self.info("📚 AVAILABLE COMMANDS")
        self._show_command_list()
        
        self.info("🔍 HELP TOPICS")
        self._show_help_topics()
        
        self.info("💡 EXAMPLES")
        self.info("• Get help for a specific command: silan help db-sync")
        self.info("• See workflow examples:          silan help workflows")
        self.info("• Troubleshoot issues:           silan help troubleshooting")
        
        return True
    
    def show_topic_help(self, topic: str) -> bool:
        """Show help for a specific topic"""
        topic_lower = topic.lower()
        
        if topic_lower not in self.help_topics:
            self.error(f"Unknown help topic: {topic}")
            self.info("Available topics:")
            for topic_name, topic_info in self.help_topics.items():
                self.info(f"  {topic_name}: {topic_info['description']}")
            return False
        
        topic_info = self.help_topics[topic_lower]
        
        self.banner("HELP", topic_info["title"], topic_info["description"])
        self.info(topic_info["content"])
        
        return True
    
    def _show_command_list(self) -> None:
        """Show list of available commands"""
        commands = [
            ("init", "Initialize a new project with content templates"),
            ("db-sync", "Sync markdown content to database"),
            ("db-config", "Manage database configuration"),
            ("backend", "Manage the Go backend server"),
            ("status", "Show project and system status"),
            ("help", "Show this help message")
        ]
        
        for cmd, desc in commands:
            self.info(f"  {cmd:<12} {desc}")
    
    def _show_help_topics(self) -> None:
        """Show available help topics"""
        for topic_name, topic_info in self.help_topics.items():
            if topic_name != "general":
                self.info(f"  {topic_name:<15} {topic_info['description']}")
    
    def _get_general_help_content(self) -> str:
        return "This is the general help content."
    
    def _get_init_help_content(self) -> str:
        return """🚀 PROJECT INITIALIZATION

USAGE:
  silan init PROJECT_NAME [OPTIONS]

DESCRIPTION:
  Initialize a new project with content templates and configuration files.
  Creates a structured directory layout optimized for content management.

OPTIONS:
  --language LANG          Default language for content (en, zh, both) [default: en]
  --with-backend           Initialize with Go backend configuration

EXAMPLES:
  silan init my-blog                    # Basic project initialization
  silan init my-portfolio --language both  # Multi-language project
  silan init my-site --with-backend     # Project with backend setup

CREATED STRUCTURE:
  my-project/
  ├── content/
  │   ├── blog/
  │   ├── projects/
  │   └── resume/
  ├── templates/
  ├── config/
  └── README.md

NEXT STEPS:
  1. cd my-project
  2. silan db-config interactive
  3. Add your content files
  4. silan db-sync"""
    
    def _get_db_sync_help_content(self) -> str:
        return """🔄 DATABASE SYNCHRONIZATION

USAGE:
  silan db-sync [OPTIONS]

DESCRIPTION:
  Sync markdown content files to your configured database.
  Automatically detects content types and creates appropriate database records.

OPTIONS:
  --db-type TYPE           Database type (mysql, postgresql, sqlite)
  --host HOST             Database host [default: localhost]
  --port PORT             Database port
  --user USER             Database username
  --password PASSWORD     Database password
  --database DATABASE     Database name
  --db-path PATH          SQLite database file path [default: portfolio.db]
  --dry-run              Show what would be synced without actually syncing
  --create-tables        Create database tables if they don't exist
  --start-backend        Start backend server after successful sync
  --use-cache            Use cached database configuration [default: true]

EXAMPLES:
  silan db-sync                        # Use cached configuration
  silan db-sync --dry-run              # Preview sync without changes
  silan db-sync --create-tables        # Create tables if missing
  silan db-sync --start-backend        # Start backend after sync
  silan db-sync --db-type sqlite --db-path ./portfolio.db

SUPPORTED CONTENT TYPES:
  • Blog posts (.md in blog/ directory)
  • Projects (.md in projects/ directory)
  • Resume/CV (.md in resume/ directory)
  • Ideas (.md in ideas/ directory)
  • Updates (.md in updates/ directory)

WORKFLOW:
  1. Scans content directories for markdown files
  2. Parses frontmatter and content structure
  3. Extracts structured data using specialized parsers
  4. Syncs to database tables with relationships
  5. Reports success/failure statistics"""
    
    def _get_db_config_help_content(self) -> str:
        return """⚙️ DATABASE CONFIGURATION

USAGE:
  silan db-config [OPTIONS]

DESCRIPTION:
  Manage database connection settings with caching for easy reuse.
  Supports MySQL, PostgreSQL, and SQLite databases.

OPTIONS:
  --action ACTION         Configuration action [default: show]
  --type TYPE            Database type (mysql, postgresql, sqlite)
  --host HOST            Database host
  --port PORT            Database port
  --user USER            Database username
  --password PASSWORD    Database password
  --database DATABASE    Database name
  --path PATH            SQLite database file path

ACTIONS:
  show                   Show current configuration
  set                    Set database configuration
  interactive            Interactive configuration setup
  cache                  Cache current configuration
  load-cache             Load cached configuration
  clear-cache            Clear cached configuration
  last-sync              Show last sync configuration
  clear-all              Clear all configurations

EXAMPLES:
  silan db-config                           # Show current config
  silan db-config interactive               # Interactive setup
  silan db-config --action set --type sqlite --path ./my-db.sqlite
  silan db-config --action cache            # Cache current config
  silan db-config --action clear-cache      # Clear cache

SQLITE SETUP:
  silan db-config --action set --type sqlite --path portfolio.db

MYSQL SETUP:
  silan db-config --action set --type mysql --host localhost --port 3306 --user root --database portfolio

POSTGRESQL SETUP:
  silan db-config --action set --type postgresql --host localhost --port 5432 --user postgres --database portfolio

CACHE LOCATION:
  Configuration is cached in: .silan/.silan_db_cache.json"""
    
    def _get_backend_help_content(self) -> str:
        return """🚀 BACKEND SERVER MANAGEMENT

USAGE:
  silan backend COMMAND [OPTIONS]

DESCRIPTION:
  Manage the Go backend server that provides API endpoints for your content.
  The backend serves your synced content through a REST API.

COMMANDS:
  start                  Start the backend server
  stop                   Stop the backend server
  restart                Restart the backend server
  status                 Show server status
  logs                   Show server logs
  install                Install/build the backend binary

START OPTIONS:
  --db-type TYPE         Database type [default: sqlite]
  --host HOST            Database host [default: localhost]
  --port PORT            Database port
  --user USER            Database username
  --password PASSWORD    Database password
  --database DATABASE    Database name
  --db-path PATH         SQLite database path [default: portfolio.db]
  --server-host HOST     Backend server host [default: 0.0.0.0]
  --server-port PORT     Backend server port [default: 8888]
  --daemon               Run as daemon process
  --config-file FILE     Custom configuration file

LOGS OPTIONS:
  --follow, -f           Follow log output
  --lines, -n NUM        Number of lines to show [default: 50]

EXAMPLES:
  silan backend start                      # Start with defaults
  silan backend start --daemon             # Start as daemon
  silan backend start --server-port 3000   # Custom port
  silan backend stop                       # Stop server
  silan backend status                     # Check status
  silan backend logs --follow              # Follow logs
  silan backend install                    # Build binary

API ENDPOINTS:
  GET /api/blog/posts              # Get blog posts
  GET /api/blog/posts/:id          # Get specific post
  GET /api/blog/series             # Get blog series
  GET /api/projects                # Get projects
  GET /api/projects/:id            # Get specific project
  GET /api/resume                  # Get resume data
  GET /api/ideas                   # Get ideas
  GET /api/updates                 # Get updates

BINARY LOCATION:
  Backend binary is built to: .silan/backend"""
    
    def _get_status_help_content(self) -> str:
        return """📊 PROJECT STATUS

USAGE:
  silan status

DESCRIPTION:
  Display comprehensive status information about your project,
  including database configuration, backend server, and content analysis.

INFORMATION DISPLAYED:
  • Project overview and configuration
  • Database connection status
  • Backend server status
  • Content files summary
  • Suggested next actions

PROJECT STATUS:
  ✅ Configuration directory exists
  ✅ Git repository detected
  📄 Important files found
  📁 Content directories detected

DATABASE STATUS:
  💾 Cached configuration details
  🔄 Last sync information
  ✅ Connection test results
  📊 Database size and statistics

BACKEND STATUS:
  🚀 Server running status
  🔗 Server URL and endpoints
  ⏱️ Uptime information
  📦 Binary availability

CONTENT ANALYSIS:
  📁 Content directories found
  📄 Markdown files count
  📊 Content type breakdown
  🏷️ Categorized by parser type

EXAMPLES:
  silan status                     # Show full status
  silan status | grep Database     # Filter database info
  silan status > status.txt        # Save to file

TROUBLESHOOTING:
  If status shows issues:
  • Missing config: Run 'silan db-config interactive'
  • Backend not running: Run 'silan backend start'
  • No content: Add .md files to content/ directory
  • Sync needed: Run 'silan db-sync'"""
    
    def _get_workflows_help_content(self) -> str:
        return """🔄 COMMON WORKFLOWS

1. NEW PROJECT SETUP:
   silan init my-project --with-backend
   cd my-project
   silan db-config interactive
   # Add your content files
   silan db-sync --create-tables
   silan backend start

2. DAILY CONTENT WORKFLOW:
   # Edit your markdown files
   silan db-sync                    # Sync changes
   silan backend restart            # Restart if needed
   silan status                     # Check everything

3. SWITCHING DATABASES:
   silan db-config --action set --type mysql --host localhost --user root --database portfolio
   silan db-config --action cache
   silan db-sync --create-tables

4. BACKUP AND RESTORE:
   silan db-config --action show > db-config-backup.txt
   # For SQLite: cp portfolio.db portfolio.db.backup
   # For MySQL/PostgreSQL: use database-specific tools

5. DEPLOYMENT WORKFLOW:
   silan db-config --action set --type postgresql --host prod-db --user app --database portfolio
   silan db-sync --create-tables
   silan backend start --daemon --server-port 8080

6. DEVELOPMENT SETUP:
   silan backend install           # Build latest binary
   silan backend start --daemon    # Start in background
   silan db-sync --dry-run        # Preview changes
   silan db-sync                  # Apply changes
   silan backend logs --follow    # Monitor logs

7. TROUBLESHOOTING WORKFLOW:
   silan status                   # Check overall status
   silan db-config --action show  # Check database config
   silan backend status           # Check backend
   silan backend logs            # Check recent logs
   silan db-sync --dry-run       # Test sync without changes"""
    
    def _get_troubleshooting_help_content(self) -> str:
        return """🔧 TROUBLESHOOTING

COMMON ISSUES AND SOLUTIONS:

1. DATABASE CONNECTION FAILED:
   Problem: "Database connection failed"
   Solutions:
   • Check database server is running
   • Verify credentials: silan db-config --action show
   • Test connection: silan db-config interactive
   • Check firewall/network settings

2. BACKEND SERVER WON'T START:
   Problem: "Failed to start backend server"
   Solutions:
   • Check if port is already in use: lsof -i :8888
   • Install/rebuild binary: silan backend install
   • Check logs: silan backend logs
   • Try different port: silan backend start --server-port 3000

3. CONTENT SYNC ERRORS:
   Problem: "DB sync command failed"
   Solutions:
   • Check content file format and frontmatter
   • Verify database tables exist: silan db-sync --create-tables
   • Use dry-run to preview: silan db-sync --dry-run
   • Check file permissions

4. BINARY NOT FOUND:
   Problem: "Backend binary not found"
   Solutions:
   • Install Go compiler
   • Build binary: silan backend install
   • Check go-server source exists
   • Verify PATH includes go

5. PERMISSION ERRORS:
   Problem: "Permission denied"
   Solutions:
   • Check file/directory permissions
   • Run with appropriate user
   • Check database user permissions
   • Verify write access to .silan directory

6. CACHE ISSUES:
   Problem: "Invalid cached configuration"
   Solutions:
   • Clear cache: silan db-config --action clear-cache
   • Reconfigure: silan db-config interactive
   • Check .silan directory permissions
   • Verify JSON format in cache files

7. CONTENT PARSING ERRORS:
   Problem: "Failed to parse content"
   Solutions:
   • Check markdown syntax
   • Verify frontmatter format (YAML)
   • Check file encoding (UTF-8)
   • Test with simple content first

8. BACKEND API ERRORS:
   Problem: "API endpoints not responding"
   Solutions:
   • Check server status: silan backend status
   • Verify database sync: silan db-sync
   • Check logs: silan backend logs
   • Test with curl: curl http://localhost:8888/api/blog/posts

DEBUGGING COMMANDS:
  silan status                     # Overall system status
  silan db-config --action show    # Database configuration
  silan backend status             # Backend server status
  silan backend logs              # Backend logs
  silan db-sync --dry-run         # Preview sync operations

LOG LOCATIONS:
  • Backend logs: .silan/backend.log
  • Database cache: .silan/.silan_db_cache.json
  • Last sync: .silan/.silan_last_sync.json

GETTING HELP:
  • Use 'silan help TOPIC' for specific help
  • Check GitHub issues for known problems
  • Run with --verbose for detailed output"""