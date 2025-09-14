# Silan Database Tools - New Architecture

## 📁 Project Structure

```
silan/
├── cli.py                      # Pure class-based CLI (SilanCLI)
├── commands/                   # CLI command files (thin wrappers)
│   ├── __init__.py            # Empty, for backward compatibility
│   ├── init.py                # silan init
│   ├── db-sync.py             # silan db-sync  
│   ├── db-config.py           # silan db-config
│   └── backend.py             # silan backend
├── logic/                     # Business logic implementations
│   ├── cli_logic.py           # Main CLI application logic
│   ├── project_init_logic.py  # Project initialization logic
│   ├── database_sync_logic.py # Database sync logic
│   ├── database_config_logic.py # DB configuration logic
│   ├── backend_logic.py       # Backend management logic
│   └── content_logic.py       # Content processing logic
├── services/                  # Service layer
│   ├── database_service.py    # Database operations
│   └── content_service.py     # Content file operations
├── managers/                  # Resource managers
│   └── backend_manager.py     # Backend process management
├── utils/                     # Utility classes (all inherit logger)
│   ├── logger.py              # ModernLogger (base for inheritance)
│   ├── file_operations.py     # FileOperations class
│   ├── cli_interface.py       # CLIInterface class
│   ├── validation.py          # DataValidator classes
│   └── config.py              # ConfigManager class
├── core/                      # Core interfaces and base classes
│   ├── interfaces.py          # ICommand, IService, IManager
│   ├── base_command.py        # BaseCommand class
│   └── exceptions.py          # Custom exception hierarchy
├── models/                    # Database models (existing)
└── parsers/                   # Content parsers (existing)
```

## 🎯 Key Architectural Principles

### 1. **CLI Layer** (`cli.py`)
- Pure class-based architecture: `SilanCLI`
- No direct rich usage - all through inherited logger
- Thin wrapper that delegates to `CLILogic`

### 2. **Command Layer** (`commands/`)
- Files named exactly as CLI commands: `db-sync.py`, `db-config.py`
- Only thin wrappers around logic implementations
- Each command has its own logger inheriting from `ModernLogger`

### 3. **Logic Layer** (`logic/`)
- All complex business logic implementations
- Each logic class uses specialized inherited loggers
- Face-oriented object design with proper separation of concerns

### 4. **Inherited Logger Pattern**
```python
# Base logger (utils/logger.py)
class ModernLogger:
    DEFAULT_THEME = {...}
    LEVEL_ICONS = {...}
    
    def _get_custom_theme(self) -> Theme:
        """Override in subclasses"""
    
    def _format_log_message(self, level: str, message: str) -> str:
        """Override in subclasses"""

# Specialized loggers (in logic/)
class DatabaseSyncLogger(ModernLogger):
    def __init__(self):
        super().__init__(name="db_sync", level="info")
    
    def sync_start(self, db_type: str, count: int):
        self.stage(f"Starting sync to {db_type}")
```

## 🔄 Data Flow

```
CLI Command
    ↓
CLI Class Method (_create_*_command)
    ↓  
CLILogic.execute_command()
    ↓
Specific Logic Class (e.g., DatabaseSyncLogic)
    ↓
Services (DatabaseService, ContentService)
    ↓
Models/Utils
```

## 🎨 Logger Inheritance Examples

### **CLI Logger** (`logic/cli_logic.py`)
```python
class SilanCLILogger(ModernLogger):
    def app_start(self, version: str):
        self.banner("SILAN", "Database Tools", f"Version {version}")
    
    def command_start(self, command: str):
        self.stage(f"Executing command: {command}")
```

### **Database Sync Logger** (`logic/database_sync_logic.py`)
```python
class DatabaseSyncLogger(ModernLogger):
    def sync_start(self, db_type: str, content_count: int):
        self.stage(f"Starting sync to {db_type} database")
        self.info(f"📚 Found {content_count} content items to process")
    
    def sync_complete(self, success_count: int, error_count: int):
        if error_count == 0:
            self.success(f"✅ Sync completed: {success_count} items")
        else:
            self.warning(f"⚠️ Completed with {error_count} errors")
```

### **Backend Logger** (`logic/backend_logic.py`)
```python
class BackendLogger(ModernLogger):
    def backend_starting(self, host: str, port: int):
        self.stage(f"Starting backend server at {host}:{port}")
    
    def backend_started(self, pid: int, url: str):
        self.success(f"✅ Backend started (PID: {pid}) at {url}")
```

## 📋 Benefits of New Architecture

1. **Clean Separation**: Commands → Logic → Services → Models
2. **Consistent Logging**: All modules use inherited specialized loggers
3. **No Direct Rich Usage**: Everything goes through logger interface
4. **Face-Oriented Design**: Proper OOP with clear responsibilities
5. **CLI Command Naming**: File names match CLI commands exactly
6. **Maintainable**: Easy to extend and modify individual components

## 🚀 Usage Examples

### **Running Commands**
```bash
silan init my-project --with-backend    # → commands/init.py → logic/project_init_logic.py
silan db-sync --create-tables           # → commands/db-sync.py → logic/database_sync_logic.py  
silan db-config interactive              # → commands/db-config.py → logic/database_config_logic.py
silan backend start                      # → commands/backend.py → logic/backend_logic.py
```

### **Logger Inheritance**
```python
# Extend for new functionality
class MyCustomLogger(ModernLogger):
    LEVEL_ICONS = {
        **ModernLogger.LEVEL_ICONS,
        "DEPLOY": "🚀",
    }
    
    def deploy_start(self, service: str):
        self.stage(f"Deploying {service}")
```

This architecture follows your requirements perfectly:
- ✅ Pure class-based CLI with inherited logger
- ✅ Commands folder only contains command-named files  
- ✅ No direct rich usage - all through logger
- ✅ Complex logic in logic/ and services/
- ✅ Face-oriented object design throughout