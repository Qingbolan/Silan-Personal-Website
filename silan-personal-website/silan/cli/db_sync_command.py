"""Database synchronization command implementation with pipeline orchestration."""

from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Union

from ..logic.database_sync_logic import DatabaseSyncLogic
from ..utils import ModernLogger


class DbSyncCommandLogger(ModernLogger):
    """Logger for db-sync command"""

    def __init__(self) -> None:
        super().__init__(name="db_sync_cmd", level="info")


PipelineStep = Tuple[str, Callable[[], Optional[bool]]]


def _run_pipeline(logger: ModernLogger, steps: Iterable[PipelineStep]) -> bool:
    """Execute pipeline steps sequentially with consistent logging."""

    for step_name, callback in steps:
        logger.debug(f"Running step: {step_name}")

        try:
            outcome = callback()
        except Exception as exc:  # noqa: BLE001 - surface any failure here
            logger.error(f"{step_name.capitalize()} failed: {exc}")
            return False

        # Treat None as success to support steps that only perform side effects
        if isinstance(outcome, bool) and not outcome:
            logger.error(f"Step '{step_name}' did not complete successfully")
            return False

    return True


def execute_db_sync_command(database_config: Union[str, Dict[str, Any]],
                           dry_run: bool = False,
                           create_tables: bool = False,
                           start_backend: bool = False,
                           logger: Optional[ModernLogger] = None) -> bool:
    """Execute the db-sync command using a pipeline of discrete steps."""

    cmd_logger = logger or DbSyncCommandLogger()
    sync_logic = DatabaseSyncLogic(database_config, dry_run)

    def _show_overview() -> Optional[bool]:
        sync_logic.show_sync_overview()
        if not dry_run:
            cmd_logger.info("Proceed with database synchronization? (y/N)")
            # CLI layer can capture actual confirmation input if needed
        return None

    steps: Iterable[PipelineStep] = (
        ("validate configuration", sync_logic.validate_configuration),
        ("show sync overview", _show_overview),
        ("execute database sync", lambda: sync_logic.execute_sync(create_tables=create_tables)),
    )

    success = _run_pipeline(cmd_logger, steps)

    if success and start_backend and not dry_run:
        cmd_logger.info("🚀 Starting backend server after sync...")
        # CLI logic orchestrates the backend start to keep responsibilities separate

    return success


# Backward compatibility
class DbSyncCommand:
    """Legacy DbSyncCommand class for backward compatibility"""

    def __init__(self, database_config: Union[str, Dict[str, Any]], dry_run: bool = False,
                 create_tables: bool = False, start_backend: bool = False) -> None:
        self.database_config = database_config
        self.dry_run = dry_run
        self.create_tables = create_tables
        self.start_backend = start_backend

    def execute(self) -> bool:
        """Execute using new logic"""
        return execute_db_sync_command(
            self.database_config,
            dry_run=self.dry_run,
            create_tables=self.create_tables,
            start_backend=self.start_backend,
        )
