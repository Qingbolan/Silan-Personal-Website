"""Core workflow for project initialization."""

from pathlib import Path
from typing import Dict, List, cast

from rich.progress import TaskID

from ...core.exceptions import ValidationError
from ...utils import CLIInterface, DataValidator, FileOperations
from .logger import ProjectInitLogger


class ProjectInitBase(ProjectInitLogger):
    """Shared workflow, validation, and orchestration helpers."""

    def __init__(self, project_name: str, language: str = "en", with_backend: bool = False) -> None:
        super().__init__()
        self.project_name = project_name
        self.language = language
        self.with_backend = with_backend
        self.file_ops = FileOperations(self)
        self.cli = CLIInterface(self)

        # Paths
        self.current_dir = Path.cwd()
        self.project_root = self.current_dir / self.project_name

        # Directory structure configuration
        self.content_dirs = [
            "content",
            "content/blog",
            "content/projects",
            "content/ideas",
            "content/moment",
            "content/episode",
            "content/resume",
        ]

        self.template_dirs = [
            "templates",
            "templates/blog",
            "templates/projects",
            "templates/ideas",
            "templates/moment",
            "templates/episode",
            "templates/resume",
        ]

        self.config_dirs = [
            ".silan",
            ".silan/temp",
            ".silan/cache",
        ]

    def validate_project_setup(self) -> bool:
        """Validate project initialization parameters."""
        try:
            # Validate project name
            self.project_name = DataValidator.validate_required_string(
                self.project_name,
                "project_name",
                min_length=2,
            )

            # Check for valid characters in project name
            if not self.project_name.replace("-", "").replace("_", "").replace(".", "").isalnum():
                raise ValidationError(
                    "Project name can only contain letters, numbers, hyphens, underscores, and dots"
                )

            # Validate language
            self.language = DataValidator.validate_choice(
                self.language,
                "language",
                ["en", "zh", "both"],
            )

            # Check if target directory exists
            if self.project_root.exists():
                if not self._handle_existing_directory():
                    return False

            return True

        except ValidationError as err:
            self.error(f"Validation failed: {err.message}")
            return False

    def _handle_existing_directory(self) -> bool:
        """Handle cases where the target directory already exists."""
        if any(self.project_root.iterdir()):
            # Directory is not empty
            self.cli.display_info_panel(
                "Directory Already Exists",
                {
                    "Path": str(self.project_root),
                    "Status": "Not empty",
                    "Warning": "Existing files may be overwritten",
                },
            )

            return self.cli.confirm(
                f"Directory '{self.project_name}' exists and is not empty. Continue anyway?",
                default=False,
            )

        # Directory exists but is empty
        return self.cli.confirm(
            f"Directory '{self.project_name}' already exists (empty). Continue?",
            default=True,
        )

    def show_initialization_plan(self) -> None:
        """Display a summary of the planned initialization steps."""
        self.section("Project Initialization Plan")

        config_info = {
            "Project Name": self.project_name,
            "Language": self.language,
            "Backend Support": "Yes" if self.with_backend else "No",
            "Target Directory": str(self.project_root),
        }
        self.cli.display_info_panel("Project Configuration", config_info)

        structure = self._get_directory_structure_preview()
        self.info("📁 Directory structure to be created:")
        for item in structure[:15]:
            self.print(f"  {item}")
        if len(structure) > 15:
            self.print(f"  ... and {len(structure) - 15} more items")

        features = self._get_features_overview()
        self.cli.display_info_panel("Features Included", features)

    def _get_directory_structure_preview(self) -> List[str]:
        """Build a preview of the folder layout."""
        structure = [f"{self.project_name}/"]
        structure.extend([f"├── {directory}/" for directory in self.content_dirs])
        structure.extend([f"├── {directory}/" for directory in self.template_dirs])
        structure.extend([f"├── {directory}/" for directory in self.config_dirs])
        structure.extend([
            "├── silan.yaml",
            "├── README.md",
            "└── .gitignore",
        ])
        if self.with_backend:
            structure.extend([
                "├── backend/",
                "│   └── .silan-cache",
                "└── .env.example",
            ])
        return structure

    def _get_features_overview(self) -> Dict[str, str]:
        """Summarise key project features for display."""
        features = {
            "Content Management": "Blog, Projects, Ideas, Updates",
            "Template System": "Customizable content templates",
            "Database Sync": "MySQL, PostgreSQL, SQLite support",
            "Configuration": "YAML-based project configuration",
            "CLI Tools": "Rich command-line interface",
        }
        if self.with_backend:
            features["Backend Server"] = "Go-based API server"
            features["Environment"] = "Production-ready configuration"
        return features

    def execute_initialization(self) -> bool:
        """Perform the full initialization workflow."""
        try:
            self.init_start(self.project_name)
            total_steps = 8 if self.with_backend else 6

            progress, raw_task_id = self.progress(total_steps, "Initializing project")
            task_id = cast(TaskID, raw_task_id)
            progress.start()
            try:
                self._create_project_root()
                progress.update(task_id, advance=1, description="Created project directory")

                self._create_content_directories()
                progress.update(task_id, advance=1, description="Created content structure")

                self._create_template_directories()
                progress.update(task_id, advance=1, description="Created template structure")

                self._create_config_directories()
                progress.update(task_id, advance=1, description="Created configuration structure")

                self._create_configuration_files()
                progress.update(task_id, advance=1, description="Created configuration files")

                self._create_sample_content()
                progress.update(task_id, advance=1, description="Created sample content")

                if self.with_backend:
                    self._create_backend_support()
                    progress.update(task_id, advance=1, description="Created backend support")

                self._create_additional_files()
                progress.update(task_id, advance=1, description="Created additional files")
            finally:
                progress.stop()

            self.init_complete(str(self.project_root))
            return True

        except Exception as exc:  # noqa: BLE001 - surfacing full error to caller/log
            self.error(f"Initialization failed: {exc}")
            return False

    def show_next_steps(self) -> None:
        """Guide the user through useful follow-up commands."""
        self.section("Next Steps")

        project_path = self.project_root
        next_steps = [
            f"cd {project_path}",
            "silan status",
            "silan db-config interactive",
            "silan db-sync --create-tables",
        ]
        if self.with_backend:
            next_steps.extend([
                "silan backend install",
                "silan backend start",
            ])

        success_details = {
            "Project Location": str(project_path),
            "Configuration": "silan.yaml",
            "Sample Content": "content/ directory",
            "Templates": "templates/ directory",
        }
        if self.with_backend:
            success_details["Backend Config"] = "backend/.silan-cache"
            success_details["Environment"] = ".env.example"

        self.cli.display_success_panel(
            "Project Initialized Successfully!",
            f"Your project '{self.project_name}' is ready to use.",
            success_details,
        )

        self.info("🚀 Quick start commands:")
        for step in next_steps:
            self.print(f"  {step}")

        self.info("\n💡 Additional resources:")
        self.print("  • Edit silan.yaml to customize your project")
        self.print("  • Add your content to content/ directories")
        self.print("  • Use templates in templates/ for consistent content")
        self.print("  • Run 'silan --help' for all available commands")
        if self.with_backend:
            self.print("  • Configure backend settings in backend/.silan-cache")
