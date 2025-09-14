"""Database synchronization command - db-sync"""

from typing import Dict, Any, Union, Optional

from ..logic.database_sync_logic import DatabaseSyncLogic
from ..utils import ModernLogger


class DbSyncCommandLogger(ModernLogger):
    """Logger for db-sync command"""
    
    def __init__(self):
        super().__init__(name="db_sync_cmd", level="info")


def execute_db_sync_command(database_config: Union[str, Dict[str, Any]], 
                           dry_run: bool = False, create_tables: bool = False,
                           start_backend: bool = False, logger: Optional[ModernLogger] = None) -> bool:
    """Execute the db-sync command - thin wrapper around logic"""
    cmd_logger = logger or DbSyncCommandLogger()
    
    try:
        sync_logic = DatabaseSyncLogic(database_config, dry_run, cmd_logger)
        
        if not sync_logic.validate_configuration():
            return False
        
        sync_logic.show_sync_overview()
        
        if not dry_run:
            cmd_logger.info("Proceed with database synchronization? (y/N)")
            # In CLI logic, this will be handled properly
        
        success = sync_logic.execute_sync(create_tables=create_tables)
        
        # Start backend if requested
        if start_backend and success and not dry_run:
            cmd_logger.info("🚀 Starting backend server after sync...")
            # This will be handled by CLI logic calling backend command
        
        return success
        
    except Exception as e:
        cmd_logger.error(f"DB sync command failed: {e}")
        return False


# Backward compatibility
class DbSyncCommand:
    """Legacy DbSyncCommand class for backward compatibility"""
    
    def __init__(self, database_config: Union[str, Dict[str, Any]], dry_run: bool = False, 
                 create_tables: bool = False, start_backend: bool = False):
        self.database_config = database_config
        self.dry_run = dry_run
        self.create_tables = create_tables
        self.start_backend = start_backend
    
    def execute(self) -> bool:
        """Execute using new logic"""
        return execute_db_sync_command(
            self.database_config, 
            self.dry_run, 
            self.create_tables, 
            self.start_backend
        )