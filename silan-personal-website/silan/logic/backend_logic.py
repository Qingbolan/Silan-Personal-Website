"""Backend management business logic"""

import subprocess
import time
import json
import psutil
import shutil
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..core.exceptions import ValidationError
from ..utils import ModernLogger, FileOperations, DataValidator, CLIInterface


class BackendLogic(ModernLogger):
    """Complex business logic for backend server management"""
    
    def __init__(self):
        super().__init__(name="backend", level="info")
        self.file_ops = FileOperations(self)
        self.cli = CLIInterface(self)
        
        # Configuration
        self.project_dir = Path.cwd()
        self.backend_dir = self.project_dir / "backend" / "go-server"
        self.silan_dir = self.project_dir / ".silan"
        self.pid_file = self.silan_dir / "backend.pid"
        self.log_file = self.silan_dir / "backend.log"
        self.config_file = self.silan_dir / "backend_config.json"
        
        # Ensure directories exist
        self.file_ops.ensure_directory(self.silan_dir)
    
    def backend_starting(self, host: str, port: int) -> None:
        """Log backend start"""
        self.stage(f"Starting backend server at {host}:{port}")
    
    def backend_started(self, pid: int, url: str) -> None:
        """Log successful backend start"""
        self.success(f"✅ Backend started (PID: {pid}) at {url}")
    
    def backend_stopping(self, pid: int) -> None:
        """Log backend stop"""
        self.info(f"🛑 Stopping backend server (PID: {pid})")
    
    def backend_stopped(self, pid: int) -> None:
        """Log successful backend stop"""
        self.success(f"✅ Backend stopped (PID: {pid})")
    
    def backend_install_start(self) -> None:
        """Log backend installation start"""
        self.stage("Installing/building backend binary")
    
    def backend_install_complete(self, binary_path: str) -> None:
        """Log successful backend installation"""
        self.success(f"✅ Backend binary installed: {binary_path}")
    
    def validate_action_config(self, action: str, config: Dict[str, Any]) -> bool:
        """Validate configuration for backend actions"""
        try:
            if action == 'start' and config:
                self._validate_start_config(config)
            elif action == 'logs' and config:
                self._validate_logs_config(config)
            
            return True
            
        except ValidationError as e:
            self.error(f"Configuration validation failed: {e.message}")
            return False
    
    def _validate_start_config(self, config: Dict[str, Any]) -> None:
        """Validate start configuration"""
        if 'database' in config:
            db_config = config['database']
            DataValidator.validate_dict(db_config, 'database_config')
            
            if 'type' in db_config:
                DataValidator.validate_choice(
                    db_config['type'], 'database_type',
                    ['mysql', 'postgresql', 'sqlite']
                )
        
        if 'server' in config:
            server_config = config['server']
            DataValidator.validate_dict(server_config, 'server_config')
            
            if 'host' in server_config:
                DataValidator.validate_required_string(server_config['host'], 'host')
            
            if 'port' in server_config:
                DataValidator.validate_integer(server_config['port'], 'port', 1, 65535)
    
    def _validate_logs_config(self, config: Dict[str, Any]) -> None:
        """Validate logs configuration"""
        if 'lines' in config:
            DataValidator.validate_integer(config['lines'], 'lines', 1, 10000)
    
    def start_backend(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Start the backend server"""
        try:
            config = config or {}
            
            # Check if already running
            if self._is_backend_running():
                status = self._get_backend_status()
                self.warning(f"Backend already running (PID: {status['pid']})")
                self.cli.display_info_panel(
                    "Backend Already Running",
                    {
                        "PID": status['pid'],
                        "URL": status['url'],
                        "Status": "Running"
                    }
                )
                return True
            
            # Validate backend binary exists, install if missing
            binary_path = self._get_binary_path()
            if not binary_path.exists():
                self.info("Backend binary not found, installing automatically...")
                if not self.install_backend():
                    self.error(f"Failed to install backend binary: {binary_path}")
                    self.cli.display_error_panel(
                        "Backend Installation Failed",
                        "Failed to install backend binary",
                        {
                            "Solution 1": "Run 'silan backend install' manually",
                            "Solution 2": "Check silan package installation",
                            "Solution 3": "Verify platform compatibility"
                        }
                    )
                    return False
            
            # Show start configuration
            self._show_start_configuration(config)
            
            # Prepare and start backend
            server_config = config.get('server', {})
            host = server_config.get('host', '0.0.0.0')
            port = server_config.get('port', 8888)
            
            self.backend_starting(host, port)
            
            # Build command
            cmd = self._build_start_command(binary_path, config)
            
            # Start process
            daemon_mode = config.get('daemon', False)
            process = self._start_backend_process(cmd, daemon_mode)
            
            if not process:
                return False
            
            # Save configuration and PID
            self._save_backend_config(config)
            self._save_backend_pid(process.pid)
            
            # Verify startup
            time.sleep(2)
            if process.poll() is not None:
                self.error("Backend process exited immediately")
                self._show_startup_logs()
                return False
            
            # Show success
            url = f"http://{host}:{port}"
            self.backend_started(process.pid, url)
            
            self.cli.display_success_panel(
                "Backend Started",
                "Backend server started successfully",
                {
                    "PID": process.pid,
                    "URL": url,
                    "Mode": "Daemon" if daemon_mode else "Interactive",
                    "Log File": str(self.log_file)
                }
            )
            
            return True
            
        except Exception as e:
            self.error(f"Failed to start backend: {e}")
            return False
    
    def stop_backend(self) -> bool:
        """Stop the backend server"""
        try:
            pid = self._get_backend_pid()
            if not pid:
                self.warning("No backend PID found - backend may not be running")
                return True
            
            if not self._is_process_running(pid):
                self.warning(f"Process {pid} is not running")
                self._cleanup_backend_files()
                return True
            
            self.backend_stopping(pid)
            
            # Try graceful shutdown
            try:
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    self.backend_stopped(pid)
                except psutil.TimeoutExpired:
                    # Force kill
                    self.warning("Graceful shutdown timed out, forcing kill")
                    process.kill()
                    process.wait(timeout=5)
                    self.backend_stopped(pid)
                    
            except psutil.NoSuchProcess:
                self.warning(f"Process {pid} no longer exists")
            
            # Cleanup
            self._cleanup_backend_files()
            
            self.cli.display_success_panel(
                "Backend Stopped",
                "Backend server stopped successfully",
                {"Previous PID": pid}
            )
            
            return True
            
        except Exception as e:
            self.error(f"Failed to stop backend: {e}")
            return False
    
    def restart_backend(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Restart the backend server"""
        try:
            self.info("🔄 Restarting backend server...")
            
            # Load previous config if none provided
            if not config:
                config = self._load_backend_config()
            
            # Stop current instance
            if not self.stop_backend():
                self.warning("Failed to stop cleanly, continuing with start")
            
            # Wait for cleanup
            time.sleep(2)
            
            # Start with config
            return self.start_backend(config)
            
        except Exception as e:
            self.error(f"Failed to restart backend: {e}")
            return False
    
    def show_backend_status(self) -> bool:
        """Show backend server status"""
        try:
            status = self._get_backend_status()
            
            if status['running']:
                self.cli.display_success_panel(
                    "Backend Status - Running",
                    "Backend server is currently running",
                    {
                        "PID": status['pid'],
                        "URL": status['url'],
                        "Uptime": status.get('uptime', 'Unknown'),
                        "Database": status.get('database', 'Unknown')
                    }
                )
            else:
                self.cli.display_info_panel(
                    "Backend Status - Not Running",
                    {
                        "Status": "Stopped",
                        "Last Known PID": status.get('last_pid', 'Unknown'),
                        "Log File": str(self.log_file) if self.log_file.exists() else "No logs"
                    }
                )
            
            return True
            
        except Exception as e:
            self.error(f"Failed to get backend status: {e}")
            return False
    
    def show_backend_logs(self, follow: bool = False, lines: int = 50) -> bool:
        """Show backend server logs"""
        try:
            if not self.log_file.exists():
                self.warning("No backend log file found")
                self.cli.display_info_panel(
                    "No Logs Found",
                    {
                        "Log File": str(self.log_file),
                        "Status": "File does not exist",
                        "Suggestion": "Start the backend to generate logs"
                    }
                )
                return True
            
            self.info(f"📋 Showing backend logs (last {lines} lines)")
            if follow:
                self.info("Press Ctrl+C to stop following logs")
            
            # Show logs
            if follow:
                return self._follow_logs(lines)
            else:
                return self._show_log_tail(lines)
                
        except KeyboardInterrupt:
            self.info("\\nLog following stopped")
            return True
        except Exception as e:
            self.error(f"Failed to show logs: {e}")
            return False
    
    def install_backend(self) -> bool:
        """Install/build the backend binary"""
        try:
            self.backend_install_start()
            
            # Check prerequisites
            if not self._check_install_prerequisites():
                return False
            
            # Show installation plan
            self._show_installation_plan()
            
            # Get confirmation
            if not self.cli.confirm("Proceed with backend installation?", default=True):
                self.info("Installation cancelled")
                return True
            
            # Build binary
            binary_path = self._get_binary_path()
            success = self._build_backend_binary(binary_path)
            
            if success:
                self.backend_install_complete(str(binary_path))
                
                self.cli.display_success_panel(
                    "Installation Complete",
                    "Backend binary built successfully",
                    {
                        "Binary Path": str(binary_path),
                        "Executable": "Yes",
                        "Next Step": "Run 'silan backend start' to start the server"
                    }
                )
                return True
            else:
                self.cli.display_error_panel(
                    "Installation Failed",
                    "Failed to build backend binary",
                    {
                        "Solution 1": "Check Go installation",
                        "Solution 2": "Verify source code integrity",
                        "Solution 3": "Check build dependencies",
                        "Solution 4": "Review error messages above"
                    }
                )
                return False
                
        except Exception as e:
            self.error(f"Failed to install backend: {e}")
            return False
    
    def _is_backend_running(self) -> bool:
        """Check if backend is currently running"""
        pid = self._get_backend_pid()
        return pid is not None and self._is_process_running(pid)
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if process with PID is running"""
        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False
    
    def _get_backend_status(self) -> Dict[str, Any]:
        """Get detailed backend status"""
        try:
            pid = self._get_backend_pid()
            
            if not pid or not self._is_process_running(pid):
                return {
                    'running': False,
                    'pid': None,
                    'url': None,
                    'last_pid': pid
                }
            
            # Get configuration
            config = self._load_backend_config()
            server_config = config.get('server', {})
            host = server_config.get('host', '0.0.0.0')
            port = server_config.get('port', 8888)
            
            # Calculate uptime
            uptime = 'Unknown'
            try:
                process = psutil.Process(pid)
                create_time = process.create_time()
                uptime_seconds = time.time() - create_time
                uptime = self._format_uptime(uptime_seconds)
            except Exception:
                pass
            
            # Database info
            db_config = config.get('database', {})
            database = self._format_database_info(db_config)
            
            return {
                'running': True,
                'pid': pid,
                'url': f"http://{host}:{port}",
                'uptime': uptime,
                'database': database
            }
            
        except Exception as e:
            self.error(f"Failed to get backend status: {e}")
            return {'running': False, 'error': str(e)}
    
    def _get_binary_path(self) -> Path:
        """Get path to backend binary"""
        return self.silan_dir / "backend"
    
    def _build_start_command(self, binary_path: Path, config: Dict[str, Any]) -> List[str]:
        """Build command to start backend"""
        cmd = [str(binary_path)]
        
        # Database configuration
        if 'database' in config:
            db_config = config['database']
            db_type = db_config.get('type', 'sqlite')
            
            if db_type == 'sqlite':
                # For SQLite, use --db-driver and --db-source
                cmd.extend(['--db-driver', 'sqlite3'])
                cmd.extend(['--db-source', db_config.get('path', 'portfolio.db')])
            else:
                # For other databases
                cmd.extend(['--db-driver', db_type])
                if 'host' in db_config:
                    cmd.extend(['--db-host', db_config['host']])
                if 'port' in db_config:
                    cmd.extend(['--db-port', str(db_config['port'])])
                if 'user' in db_config:
                    cmd.extend(['--db-user', db_config['user']])
                if 'password' in db_config:
                    cmd.extend(['--db-password', db_config['password']])
                if 'database' in db_config:
                    cmd.extend(['--db-name', db_config['database']])
        else:
            # Default SQLite configuration
            cmd.extend(['--db-driver', 'sqlite3'])
            cmd.extend(['--db-source', 'portfolio.db'])
        
        # Server configuration
        if 'server' in config:
            server_config = config['server']
            if 'host' in server_config:
                cmd.extend(['--host', server_config['host']])
            if 'port' in server_config:
                cmd.extend(['--port', str(server_config['port'])])
        
        return cmd
    
    def _start_backend_process(self, cmd: List[str], daemon_mode: bool) -> Optional[subprocess.Popen]:
        """Start backend process"""
        try:
            if daemon_mode:
                # Start as daemon
                process = subprocess.Popen(
                    cmd,
                    stdout=open(self.log_file, 'a'),
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    cwd=self.project_dir
                )
            else:
                # Start in foreground
                process = subprocess.Popen(
                    cmd,
                    stdout=open(self.log_file, 'a'),
                    stderr=subprocess.STDOUT,
                    cwd=self.project_dir
                )
            
            return process
            
        except Exception as e:
            self.error(f"Failed to start backend process: {e}")
            return None
    
    def _show_start_configuration(self, config: Dict[str, Any]) -> None:
        """Show backend start configuration"""
        if not config:
            return
        
        config_display = {}
        
        # Database configuration
        if 'database' in config:
            db_config = config['database']
            config_display['Database Type'] = db_config.get('type', 'sqlite').upper()
            
            if db_config.get('type') == 'sqlite':
                config_display['Database File'] = db_config.get('path', 'portfolio.db')
            else:
                host = db_config.get('host', 'localhost')
                port = db_config.get('port', 'default')
                config_display['Database Host'] = f"{host}:{port}"
                config_display['Database Name'] = db_config.get('database', 'Unknown')
        
        # Server configuration
        if 'server' in config:
            server_config = config['server']
            host = server_config.get('host', '0.0.0.0')
            port = server_config.get('port', 8888)
            config_display['Server URL'] = f"http://{host}:{port}"
        
        config_display['Mode'] = 'Daemon' if config.get('daemon', False) else 'Interactive'
        
        if config_display:
            self.cli.display_info_panel("Backend Configuration", config_display)
    
    def _show_installation_plan(self) -> None:
        """Show backend installation plan"""
        precompiled_binary = self._get_precompiled_binary_path()
        plan = {
            "Source Binary": str(precompiled_binary) if precompiled_binary else "Not found",
            "Target Binary": str(self._get_binary_path()),
            "Installation Method": "Copy precompiled binary",
            "Platform": f"{platform.system()} {platform.machine()}"
        }
        
        self.cli.display_info_panel("Installation Plan", plan)
    
    def _check_install_prerequisites(self) -> bool:
        """Check installation prerequisites"""
        try:
            # Check if precompiled binary exists
            precompiled_binary = self._get_precompiled_binary_path()
            if not precompiled_binary or not precompiled_binary.exists():
                self.error("Precompiled backend binary not found in silan package")
                return False
            
            self.debug(f"Found precompiled binary: {precompiled_binary}")
            return True
            
        except Exception as e:
            self.error(f"Prerequisites check failed: {e}")
            return False
    
    def _build_backend_binary(self, binary_path: Path) -> bool:
        """Install the backend binary by copying from precompiled binaries"""
        try:
            # Ensure target directory exists
            self.file_ops.ensure_directory(binary_path.parent)
            
            # Get precompiled binary path
            source_binary = self._get_precompiled_binary_path()
            if not source_binary or not source_binary.exists():
                self.error("Precompiled backend binary not found")
                return False
            
            # Copy binary to target location
            shutil.copy2(source_binary, binary_path)
            
            # Make executable
            binary_path.chmod(0o755)
            self.debug(f"Backend binary installed successfully: {binary_path}")
            return True
                
        except Exception as e:
            self.error(f"Failed to install backend binary: {e}")
            return False
    
    def _get_precompiled_binary_path(self) -> Optional[Path]:
        """Get path to precompiled backend binary based on platform"""
        try:
            # Get silan package installation directory
            import silan
            silan_dir = Path(silan.__file__).parent
            bin_dir = silan_dir / "server" / "bin"
            
            # Platform-specific binary name
            system = platform.system().lower()
            arch = platform.machine().lower()
            
            # Map platform to binary name
            if system == "darwin":  # macOS
                binary_name = "silan-backend"
            elif system == "linux":
                binary_name = "silan-backend"
            elif system == "windows":
                binary_name = "silan-backend.exe"
            else:
                self.error(f"Unsupported platform: {system}")
                return None
            
            binary_path = bin_dir / binary_name
            return binary_path if binary_path.exists() else None
            
        except Exception as e:
            self.error(f"Failed to locate precompiled binary: {e}")
            return None

    def _get_backend_pid(self) -> Optional[int]:
        """Get backend PID from file"""
        try:
            if self.pid_file.exists():
                content = self.file_ops.read_file(self.pid_file).strip()
                return int(content) if content.isdigit() else None
        except Exception:
            pass
        return None
    
    def _save_backend_pid(self, pid: int) -> None:
        """Save backend PID to file"""
        self.file_ops.write_file(self.pid_file, str(pid))
    
    def _save_backend_config(self, config: Dict[str, Any]) -> None:
        """Save backend configuration"""
        try:
            config_json = json.dumps(config, indent=2)
            self.file_ops.write_file(self.config_file, config_json)
        except Exception as e:
            self.error(f"Failed to save backend config: {e}")
    
    def _load_backend_config(self) -> Dict[str, Any]:
        """Load backend configuration"""
        try:
            if self.config_file.exists():
                config_json = self.file_ops.read_file(self.config_file)
                return json.loads(config_json)
        except Exception as e:
            self.error(f"Failed to load backend config: {e}")
        return {}
    
    def _cleanup_backend_files(self) -> None:
        """Clean up backend PID and config files"""
        try:
            if self.pid_file.exists():
                self.file_ops.delete_file(self.pid_file)
        except Exception as e:
            self.error(f"Failed to cleanup backend files: {e}")
    
    def _show_startup_logs(self) -> None:
        """Show recent startup logs for debugging"""
        try:
            if self.log_file.exists():
                self.error("Recent backend logs:")
                self._show_log_tail(10)
        except Exception:
            pass
    
    def _show_log_tail(self, lines: int) -> bool:
        """Show last N lines of logs"""
        try:
            # Try using tail command first
            try:
                result = subprocess.run(
                    ['tail', '-n', str(lines), str(self.log_file)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(result.stdout)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python implementation
                with open(self.log_file, 'r') as f:
                    all_lines = f.readlines()
                    for line in all_lines[-lines:]:
                        print(line.rstrip())
                return True
                
        except Exception as e:
            self.error(f"Failed to show log tail: {e}")
            return False
    
    def _follow_logs(self, lines: int) -> bool:
        """Follow logs in real-time"""
        try:
            # Show initial lines
            self._show_log_tail(lines)
            
            # Follow new lines
            process = subprocess.Popen(
                ['tail', '-f', str(self.log_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.stdout is None:
                self.error("Failed to capture stdout from tail process")
                return False
            
            try:
                for line in process.stdout:
                    print(line.rstrip())
            except KeyboardInterrupt:
                process.terminate()
                return True
            
            return True
                
        except Exception as e:
            self.error(f"Failed to follow logs: {e}")
            return False
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _format_database_info(self, db_config: Dict[str, Any]) -> str:
        """Format database info for display"""
        if not db_config:
            return "Unknown"
        
        db_type = db_config.get('type', 'unknown')
        if db_type == 'sqlite':
            return f"SQLite ({db_config.get('path', 'portfolio.db')})"
        else:
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 'default')
            return f"{db_type.upper()} ({host}:{port})"