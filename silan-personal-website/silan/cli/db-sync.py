"""Compatibility wrapper for db-sync command module.

This file keeps the original CLI command filename (`db-sync.py`) while
delegating the actual implementation to `db_sync_command.py` so that the
logic can be imported using a valid Python module name.
"""

from .db_sync_command import DbSyncCommand, execute_db_sync_command

__all__ = ["execute_db_sync_command", "DbSyncCommand"]
