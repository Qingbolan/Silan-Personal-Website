"""Backend manager for Go server lifecycle management"""

import subprocess
import time
import json
import psutil
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.interfaces import IManager
from ..utils import ModernLogger, FileOperations


class BackendManager(IManager,ModernLogger):
    """Manager for Go backend server lifecycle and operations"""
    
    def __init__(self):
        super().__init__(name="backend_manager", level="info")
        self.file_ops = FileOperations(self)
        
        # Configuration
        self.project_dir = Path.cwd()
        self.backend_dir = self.project_dir / "backend"
        self.pid_file = self.project_dir / ".silan" / "backend.pid"
        self.log_file = self.project_dir / ".silan" / "backend.log"
        self.config_file = self.project_dir / ".silan" / "backend_config.json"
        
        # Ensure directories exist
        self.file_ops.ensure_directory(self.pid_file.parent)
    
    def start(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Start the Go backend server"""
        try:
            # Check if already running
            if self._is_running():
                self.warning("Backend server is already running")
                return True
            
            # Get backend binary path
            binary_path = self.get_binary_path()
            if not binary_path.exists():
                self.error(f"Backend binary not found: {binary_path}")
                self.info("Run 'silan backend install' to build the backend")
                return False
            
            # Prepare configuration
            config = config or {}
            self._save_config(config)
            
            # Prepare command
            cmd = [str(binary_path)]
            
            # Add configuration arguments
            if 'database' in config:
                db_config = config['database']
                cmd.extend(['--db-type', db_config.get('type', 'sqlite')])
                
                if db_config.get('type') == 'sqlite':
                    cmd.extend(['--db-path', db_config.get('path', 'portfolio.db')])
                else:
                    cmd.extend(['--db-host', db_config.get('host', 'localhost')])
                    cmd.extend(['--db-port', str(db_config.get('port', 3306 if db_config.get('type') == 'mysql' else 5432))])
                    cmd.extend(['--db-user', db_config.get('user', '')])
                    cmd.extend(['--db-password', db_config.get('password', '')])
                    cmd.extend(['--db-name', db_config.get('database', '')])
            
            if 'server' in config:
                server_config = config['server']
                cmd.extend(['--host', server_config.get('host', '0.0.0.0')])
                cmd.extend(['--port', str(server_config.get('port', 8888))])
            
            # Start the process
            daemon_mode = config.get('daemon', False)
            
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
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=self.project_dir
                )
            
            # Save PID
            self._save_pid(process.pid)
            
            # Wait a moment and check if process is still running
            time.sleep(2)
            if process.poll() is not None:
                self.error("Backend process exited immediately")
                return False
            
            self.info(f"✅ Backend server started (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.error(f"Failed to start backend: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the Go backend server"""
        try:
            pid = self._get_pid()
            if not pid:
                self.warning("No backend PID found")
                return True
            
            # Check if process exists
            if not self._is_process_running(pid):
                self.warning(f"Process {pid} is not running")
                self._cleanup_pid_file()
                return True
            
            # Try graceful shutdown first
            try:
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    self.info(f"✅ Backend server stopped gracefully (PID: {pid})")
                except psutil.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.warning("Graceful shutdown timed out, forcing kill")
                    process.kill()
                    process.wait(timeout=5)
                    self.info(f"✅ Backend server force stopped (PID: {pid})")
                
            except psutil.NoSuchProcess:
                self.warning(f"Process {pid} no longer exists")
            
            # Cleanup
            self._cleanup_pid_file()
            return True
            
        except Exception as e:
            self.error(f"Failed to stop backend: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the Go backend server"""
        try:
            # Load previous config
            config = self._load_config()
            
            # Stop current instance
            if not self.stop():
                self.warning("Failed to stop cleanly, continuing with start")
            
            # Wait a moment
            time.sleep(2)
            
            # Start with previous config
            return self.start(config)
            
        except Exception as e:
            self.error(f"Failed to restart backend: {e}")
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get backend server status information"""
        try:
            pid = self._get_pid()
            
            if not pid or not self._is_process_running(pid):
                return {
                    'running': False,
                    'pid': None,
                    'url': None,
                    'last_pid': pid
                }
            
            # Get process info
            config = self._load_config()
            server_config = config.get('server', {})
            host = server_config.get('host', '0.0.0.0')
            port = server_config.get('port', 8888)
            
            # Calculate uptime
            try:
                process = psutil.Process(pid)
                create_time = process.create_time()
                uptime_seconds = time.time() - create_time
                uptime = self._format_uptime(uptime_seconds)
            except:
                uptime = 'Unknown'
            
            # Database info
            db_config = config.get('database', {})
            db_info = f"{db_config.get('type', 'unknown')}"
            if db_config.get('type') == 'sqlite':
                db_info += f" ({db_config.get('path', 'portfolio.db')})"
            else:
                db_info += f" ({db_config.get('host', 'localhost')}:{db_config.get('port', 'default')})"
            
            return {
                'running': True,
                'pid': pid,
                'url': f"http://{host}:{port}",
                'database': db_info,
                'uptime': uptime
            }
            
        except Exception as e:
            self.error(f"Failed to get status: {e}")
            return {'running': False, 'error': str(e)}
    
    def show_logs(self, follow: bool = False, lines: int = 50) -> bool:
        """Show backend server logs"""
        try:
            if not self.log_file.exists():
                self.warning("No log file found")
                return True
            
            if follow:
                # Follow logs in real-time
                try:
                    process = subprocess.Popen(
                        ['tail', '-f', '-n', str(lines), str(self.log_file)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    for line in process.stdout or []:
                        print(line.rstrip())
                        
                except KeyboardInterrupt:
                    process.terminate()
                    return True
            else:
                # Show last N lines
                try:
                    result = subprocess.run(
                        ['tail', '-n', str(lines), str(self.log_file)],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(result.stdout)
                except subprocess.CalledProcessError:
                    # Fallback to Python implementation
                    with open(self.log_file, 'r') as f:
                        all_lines = f.readlines()
                        for line in all_lines[-lines:]:
                            print(line.rstrip())
            
            return True
            
        except Exception as e:
            self.error(f"Failed to show logs: {e}")
            return False
    
    def install_backend(self) -> bool:
        """Install/build the Go backend binary"""
        try:
            # Check if Go is available
            try:
                subprocess.run(['go', 'version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.error("Go compiler not found. Please install Go first.")
                return False
            
            # Check if source exists
            if not self.backend_dir.exists():
                self.error(f"Backend source directory not found: {self.backend_dir}")
                return False
            
            go_mod_file = self.backend_dir / "go.mod"
            if not go_mod_file.exists():
                self.error(f"No go.mod file found in {self.backend_dir}")
                return False
            
            # Build binary
            binary_path = self.get_binary_path()
            self.file_ops.ensure_directory(binary_path.parent)
            
            self.info("🔨 Building Go backend...")
            
            build_cmd = [
                'go', 'build',
                '-o', str(binary_path),
                '.'
            ]
            
            result = subprocess.run(
                build_cmd,
                cwd=self.backend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Make binary executable
                binary_path.chmod(0o755)
                self.success(f"Backend binary built: {binary_path}")
                return True
            else:
                self.error(f"Build failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.error(f"Failed to install backend: {e}")
            return False
    
    def get_binary_path(self) -> Path:
        """Get the path to the backend binary"""
        return self.project_dir / ".silan" / "backend"
    
    def _is_running(self) -> bool:
        """Check if backend is currently running"""
        pid = self._get_pid()
        return pid is not None and self._is_process_running(pid)
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running"""
        try:
            return psutil.pid_exists(pid)
        except:
            return False
    
    def _get_pid(self) -> Optional[int]:
        """Get the PID from the PID file"""
        try:
            if self.pid_file.exists():
                content = self.file_ops.read_file(self.pid_file).strip()
                return int(content) if content.isdigit() else None
        except:
            pass
        return None
    
    def _save_pid(self, pid: int) -> None:
        """Save PID to file"""
        self.file_ops.write_file(self.pid_file, str(pid))
    
    def _cleanup_pid_file(self) -> None:
        """Remove PID file"""
        try:
            if self.pid_file.exists():
                self.file_ops.delete_file(self.pid_file)
        except:
            pass
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            config_json = json.dumps(config, indent=2)
            self.file_ops.write_file(self.config_file, config_json)
        except Exception as e:
            self.error(f"Failed to save config: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                config_json = self.file_ops.read_file(self.config_file)
                return json.loads(config_json)
        except Exception as e:
            self.error(f"Failed to load config: {e}")
        return {}
    
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