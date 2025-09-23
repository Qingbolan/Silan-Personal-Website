#!/usr/bin/env python3
"""
Silan Database Tools CLI

A command-line tool for syncing markdown content to databases.
Pure class-based architecture using inherited logger.
"""

import click
from typing import Optional

from pathlib import Path
from .utils.config import ConfigManager

from .logic.cli_logic import CLILogic


class SilanCLI:
    """Main CLI application class"""

    def __init__(self):
        self.cli_logic = CLILogic()

    def create_cli_group(self):
        """Create the main CLI group"""
        @click.group()
        @click.version_option(version='1.0.0')
        @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
        @click.pass_context
        def cli(ctx, verbose):
            """Silan Database Tools - Sync markdown content to databases with ease"""
            self.cli_logic.run_application(ctx, verbose)

        # Add commands to the group
        cli.add_command(self._create_init_command())
        cli.add_command(self._create_db_sync_command())
        cli.add_command(self._create_db_config_command())
        cli.add_command(self._create_backend_group())
        cli.add_command(self._create_frontend_group())

        # New content scaffolding groups
        cli.add_command(self._create_ideas_group())
        cli.add_command(self._create_projects_group())
        cli.add_command(self._create_new_command())

        cli.add_command(self._create_status_command())
        cli.add_command(self._create_help_command())

        return cli

    def _create_init_command(self):
        """Create init command"""
        @click.command()
        @click.argument('project_name')
        @click.option('--language', default='en',
                      type=click.Choice(['en', 'zh', 'both']),
                      help='Default language for content')
        @click.option('--with-backend', is_flag=True, help='Initialize with Go backend configuration')
        def init(project_name: str, language: str, with_backend: bool):
            """Initialize a new project with content templates"""
            success = self.cli_logic.execute_command(
                'init',
                project_name=project_name,
                language=language,
                with_backend=with_backend
            )
            if not success:
                raise click.ClickException("Project initialization failed")

        return init

    def _create_db_sync_command(self):
        """Create db-sync command"""
        @click.command('db-sync')
        @click.option('--db-type', default=None, type=click.Choice(['mysql', 'postgresql', 'sqlite']),
                      help='Database type (will use cached config if not specified)')
        @click.option('--host', default='localhost', help='Database host (MySQL/PostgreSQL only)')
        @click.option('--port', type=int, help='Database port (MySQL/PostgreSQL only)')
        @click.option('--user', help='Database user (MySQL/PostgreSQL only)')
        @click.option('--password', help='Database password (MySQL/PostgreSQL only)')
        @click.option('--database', help='Database name (MySQL/PostgreSQL only)')
        @click.option('--db-path', default='portfolio.db', help='Database file path (SQLite only)')
        @click.option('--dry-run', is_flag=True, help='Show what would be synced without actually syncing')
        @click.option('--create-tables', is_flag=True, help='Create database tables if they don\'t exist')
        @click.option('--start-backend', is_flag=True, help='Start backend server after sync')
        @click.option('--use-cache', is_flag=True, default=True, help='Use cached database configuration')
        def db_sync(db_type: Optional[str], host: str, port: Optional[int], user: Optional[str],
                   password: Optional[str], database: Optional[str], db_path: str, dry_run: bool,
                   create_tables: bool, start_backend: bool, use_cache: bool):
            """Sync content files to database (MySQL/PostgreSQL/SQLite)"""
            success = self.cli_logic.execute_command(
                'db-sync',
                db_type=db_type,
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                db_path=db_path,
                dry_run=dry_run,
                create_tables=create_tables,
                start_backend=start_backend,
                use_cache=use_cache
            )
            if not success:
                raise click.ClickException("Database sync failed")

        return db_sync

    def _create_db_config_command(self):
        """Create db-config command"""
        @click.command('db-config')
        @click.option('--action', default='show',
                      type=click.Choice(['show', 'set', 'cache', 'load-cache', 'clear-cache', 'interactive', 'last-sync', 'clear-all']),
                      help='Configuration action to perform')
        @click.option('--type', help='Database type (mysql, postgresql, sqlite)')
        @click.option('--host', help='Database host')
        @click.option('--port', help='Database port')
        @click.option('--user', help='Database user')
        @click.option('--password', help='Database password')
        @click.option('--database', help='Database name')
        @click.option('--path', help='SQLite database file path')
        def db_config(action: str, type: Optional[str], host: Optional[str], port: Optional[str],
                     user: Optional[str], password: Optional[str], database: Optional[str], path: Optional[str]):
            """Manage database configuration with caching"""
            params = {
                'db_type': type,
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'database': database,
                'path': path
            }
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}

            success = self.cli_logic.execute_command('db-config', action=action, **params)
            if not success:
                raise click.ClickException("Database configuration failed")

        return db_config

    def _create_backend_group(self):
        """Create backend command group"""
        @click.group()
        def backend():
            """Manage the Go backend server"""
            pass

        # Add backend subcommands
        backend.add_command(self._create_backend_start_command())
        backend.add_command(self._create_backend_stop_command())
        backend.add_command(self._create_backend_restart_command())
        backend.add_command(self._create_backend_status_command())
        backend.add_command(self._create_backend_logs_command())
        backend.add_command(self._create_backend_install_command())

        return backend

    def _create_backend_start_command(self):
        """Create backend start command"""
        @click.command('start')
        @click.option('--db-type', default='sqlite', type=click.Choice(['mysql', 'postgresql', 'sqlite']),
                      help='Database type')
        @click.option('--host', default='localhost', help='Database host (MySQL/PostgreSQL only)')
        @click.option('--port', type=int, help='Database port (MySQL/PostgreSQL only)')
        @click.option('--user', help='Database user (MySQL/PostgreSQL only)')
        @click.option('--password', help='Database password (MySQL/PostgreSQL only)')
        @click.option('--database', help='Database name (MySQL/PostgreSQL only)')
        @click.option('--db-path', default='portfolio.db', help='Database file path (SQLite only)')
        @click.option('--server-host', default='0.0.0.0', help='Backend server host')
        @click.option('--server-port', default=5200, help='Backend server port')
        @click.option('--google-client-id', help='Google OAuth Client ID (optional, passed to backend as --google-client-id)')

        @click.option('--daemon', '-d', is_flag=True, help='Run backend as daemon')
        @click.option('--config-file', help='Custom backend configuration file')
        def start(db_type: str, host: str, port: Optional[int], user: Optional[str], password: Optional[str],
                 database: Optional[str], db_path: str, server_host: str, server_port: int,
                 google_client_id: Optional[str], daemon: bool, config_file: Optional[str]):
            """Start the Go backend server"""
            # Build database configuration
            if db_type in ['mysql', 'postgresql']:
                if port is None:
                    port = 3306 if db_type == 'mysql' else 5432

                db_config = {
                    'type': db_type,
                    'host': host,
                    'port': port,
                    'user': user or ('root' if db_type == 'mysql' else 'postgres'),
                    'password': password or '',
                    'database': database or 'silan_portfolio'
                }
            else:
                db_config = {
                    'type': 'sqlite',
                    'path': db_path
                }

            # prefer CLI flag; fallback to project config (silan.yaml: auth.google_client_id)
            effective_google_client_id = google_client_id
            if not effective_google_client_id:
                try:
                    cfg = ConfigManager(Path.cwd()).load_config()
                    effective_google_client_id = cfg.get('auth', {}).get('google_client_id')
                except Exception:
                    effective_google_client_id = None

            backend_config = {
                'database': db_config,
                'server': {
                    'host': server_host,
                    'port': server_port
                },
                'auth': {
                    'google_client_id': effective_google_client_id
                },
                'daemon': daemon,
                'config_file': config_file
            }

            success = self.cli_logic.execute_command('backend', action='start', **backend_config)
            if not success:
                raise click.ClickException("Failed to start backend server")

        return start

    def _create_backend_stop_command(self):
        """Create backend stop command"""
        @click.command('stop')
        def stop():
            """Stop the Go backend server"""
            success = self.cli_logic.execute_command('backend', action='stop')
            if not success:
                raise click.ClickException("Failed to stop backend server")

        return stop

    def _create_backend_restart_command(self):
        """Create backend restart command"""
        @click.command('restart')
        def restart():
            """Restart the Go backend server"""
            success = self.cli_logic.execute_command('backend', action='restart')
            if not success:
                raise click.ClickException("Failed to restart backend server")

        return restart

    def _create_backend_status_command(self):
        """Create backend status command"""
        @click.command('status')
        def status():
            """Check the status of the Go backend server"""
            self.cli_logic.execute_command('backend', action='status')

        return status

    def _create_backend_logs_command(self):
        """Create backend logs command"""
        @click.command('logs')
        @click.option('--follow', '-f', is_flag=True, help='Follow log output')
        @click.option('--lines', '-n', default=50, help='Number of lines to show')
        def logs(follow: bool, lines: int):
            """Show backend server logs"""
            success = self.cli_logic.execute_command('backend', action='logs', follow=follow, lines=lines)
            if not success:
                raise click.ClickException("Failed to show backend logs")

        return logs

    def _create_backend_install_command(self):
        """Create backend install command"""
        @click.command('install')
        def install():
            """Install or build the Go backend binary"""
            success = self.cli_logic.execute_command('backend', action='install')
            if not success:
                raise click.ClickException("Failed to install backend binary")

        return install

    def _create_status_command(self):
        """Create status command"""
        @click.command()
        def status():
            """Show content summary and database configuration"""
            self.cli_logic.execute_command('status')

        return status

    def _create_help_command(self):
        """Create help command"""
        @click.command()
        @click.argument('topic', required=False)
        def help(topic: Optional[str]):
            """Show help information for commands and topics"""
            success = self.cli_logic.execute_command('help', topic=topic)
            if not success:
                raise click.ClickException("Help command failed")

        return help

    def _create_frontend_group(self):
        """Create frontend command group"""
        @click.group()
        def frontend():
            """Manage frontend templates and projects"""
            pass

        # Add frontend subcommands
        frontend.add_command(self._create_frontend_install_command())

        return frontend

    def _create_frontend_install_command(self):
        """Create frontend install command"""
        @click.command('install')
        @click.option('--dev', is_flag=True, help='Install full development project (default: static files)')
        @click.option('--target', help='Target directory (default: current directory)')
        def install(dev: bool, target: Optional[str]):
            """Install frontend templates to current or specified directory"""
            success = self.cli_logic.execute_command(
                'frontend',
                action='install',
                dev_mode=dev,
                target_dir=target
            )
            if not success:
                raise click.ClickException("Frontend installation failed")

        return install

    def _create_ideas_group(self):
        """Create ideas command group"""
        import click

        @click.group(name='ideas')
        def ideas():
            """Create and manage ideas content (multi-file, series, metadata)"""
            pass

        @ideas.command('create')
        @click.option('--title', required=True, help='Idea title')
        @click.option('--category', default=None, help='Idea category')
        @click.option('--tag', 'tags', multiple=True, help='Tags (repeatable)')
        @click.option('--series', default=None, help='Create a series/collection under this idea')
        @click.option('--open-collab', is_flag=True, help='Mark as open for collaboration')
        @click.option('--difficulty', default=None, help='Difficulty (e.g., easy/medium/hard)')
        @click.option('--research-field', default=None, help='Research field')
        def create(title: str, category: str | None, tags: tuple[str, ...], series: str | None,
                   open_collab: bool, difficulty: str | None, research_field: str | None):
            from .logic.content_scaffold_logic import ContentScaffoldLogic, IdeaOptions
            logic = ContentScaffoldLogic()
            opts = IdeaOptions(
                category=category,
                tags=list(tags) if tags else None,
                open_for_collaboration=open_collab,
                difficulty=difficulty,
                research_field=research_field,
                series=series,
            )
            root = logic.create_idea(title, opts)
            logic.success(f"Idea scaffold created: {root}")

        @ideas.command('episode')
        @click.option('--idea-title', required=True, help='Parent idea title (for locating folder)')
        @click.option('--series', required=True, help='Series/collection name')
        @click.option('--episode-title', required=True, help='Episode/article title')
        @click.option('--order', type=int, default=1, help='Episode order number')
        def episode(idea_title: str, series: str, episode_title: str, order: int):
            from .logic.content_scaffold_logic import ContentScaffoldLogic
            logic = ContentScaffoldLogic()
            path = logic.create_idea_episode(idea_title, series, episode_title, order)
            logic.success(f"Episode created: {path}")

        return ideas

    def _create_projects_group(self):
        """Create projects command group"""
        import click

        @click.group(name='projects')
        def projects():
            """Create and manage project scaffolds and standard files"""
            pass

        @projects.command('create')
        @click.option('--name', required=True, help='Project name')
        @click.option('--description', default=None, help='Project description')
        @click.option('--status', default='active', type=click.Choice(['active','completed','on-hold','cancelled']))
        @click.option('--tag', 'tags', multiple=True, help='Tags (repeatable)')
        @click.option('--tech', 'technologies', multiple=True, help='Technologies used (repeatable)')
        @click.option('--license', 'license_name', default='MIT', help='License name (default: MIT)')
        def create(name: str, description: str | None, status: str, tags: tuple[str, ...],
                   technologies: tuple[str, ...], license_name: str):
            from .logic.content_scaffold_logic import ContentScaffoldLogic, ProjectOptions
            logic = ContentScaffoldLogic()
            opts = ProjectOptions(
                description=description,
                tags=list(tags) if tags else None,
                status=status,
                technologies=list(technologies) if technologies else None,
                license=license_name,
            )
            root = logic.create_project(name, opts)
            logic.success(f"Project scaffold created: {root}")

        return projects

    def _create_new_command(self):
        """Create unified new command for all content types"""
        import click

        @click.command(name='new')
        @click.argument('content_type', type=click.Choice(['blog', 'project', 'idea', 'episode', 'resume']))
        @click.argument('name')
        @click.option('--title', help='Content title (defaults to name)')
        @click.option('--description', help='Content description')
        @click.option('--category', help='Content category')
        @click.option('--tag', 'tags', multiple=True, help='Tags (repeatable)')
        @click.option('--language', default='en', type=click.Choice(['en', 'zh', 'both']),
                      help='Language support (default: en)')
        @click.option('--status', help='Initial status')
        @click.option('--type', 'sub_type', help='Content subtype (e.g., vlog, tutorial)')
        def new(content_type: str, name: str, title: str, description: str, category: str,
                tags: tuple, language: str, status: str, sub_type: str):
            """Create new content of specified type"""
            success = self.cli_logic.execute_command(
                'new',
                content_type=content_type,
                name=name,
                title=title or name.replace('-', ' ').replace('_', ' ').title(),
                description=description,
                category=category,
                tags=list(tags) if tags else [],
                language=language,
                status=status,
                sub_type=sub_type
            )
            if not success:
                raise click.ClickException(f"Failed to create {content_type}: {name}")

        return new


# Create the CLI instance and get the main group
_silan_app = SilanCLI()
cli = _silan_app.create_cli_group()


if __name__ == '__main__':
    cli()