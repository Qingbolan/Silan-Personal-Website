"""Composite project initialization logic."""

from .base import ProjectInitBase
from .mixins import ProjectGenerationMixin, ProjectStructureMixin


class ProjectInitLogic(
    ProjectGenerationMixin,
    ProjectStructureMixin,
    ProjectInitBase,
):
    """Full-featured project initialization workflow."""

    pass
