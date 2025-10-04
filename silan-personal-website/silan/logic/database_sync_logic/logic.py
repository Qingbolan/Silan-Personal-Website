from .base import DatabaseSyncBase
from .mixins import (
    BlogSyncMixin,
    IdeaSyncMixin,
    ProjectSyncMixin,
    ResumeSyncMixin,
    UpdateSyncMixin,
)


class DatabaseSyncLogic(
    BlogSyncMixin,
    ProjectSyncMixin,
    IdeaSyncMixin,
    UpdateSyncMixin,
    ResumeSyncMixin,
    DatabaseSyncBase,
):
    """Database synchronization logic. inherit from base and mixins."""
    pass
