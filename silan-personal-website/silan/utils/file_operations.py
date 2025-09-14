"""File system operations utility class"""
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.exceptions import FileSystemError
from .logger import ModernLogger


class FileOperations:
    """Utility class for file system operations with error handling and logging"""
    
    def __init__(self, logger: Optional[ModernLogger] = None):
        self.logger = logger or ModernLogger(name="file_operations")
    
    def ensure_directory(self, path: Path) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Directory ensured: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {e}")
            raise FileSystemError(f"Cannot create directory: {path}", str(path))
    
    def copy_file(self, source: Path, destination: Path, overwrite: bool = False) -> bool:
        """Copy file from source to destination"""
        try:
            if destination.exists() and not overwrite:
                self.logger.warning(f"File already exists: {destination}")
                return False
            
            # Ensure destination directory exists
            self.ensure_directory(destination.parent)
            
            shutil.copy2(source, destination)
            self.logger.debug(f"File copied: {source} -> {destination}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy file: {e}")
            raise FileSystemError(f"Cannot copy file from {source} to {destination}", str(source))
    
    def move_file(self, source: Path, destination: Path, overwrite: bool = False) -> bool:
        """Move file from source to destination"""
        try:
            if destination.exists() and not overwrite:
                self.logger.warning(f"File already exists: {destination}")
                return False
            
            # Ensure destination directory exists
            self.ensure_directory(destination.parent)
            
            shutil.move(str(source), str(destination))
            self.logger.debug(f"File moved: {source} -> {destination}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to move file: {e}")
            raise FileSystemError(f"Cannot move file from {source} to {destination}", str(source))
    
    def delete_file(self, path: Path, safe: bool = True) -> bool:
        """Delete file with optional safety check"""
        try:
            if not path.exists():
                self.logger.warning(f"File does not exist: {path}")
                return False
            
            if safe and path.is_dir():
                raise FileSystemError(f"Path is a directory, not a file: {path}", str(path))
            
            path.unlink()
            self.logger.debug(f"File deleted: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file: {e}")
            raise FileSystemError(f"Cannot delete file: {path}", str(path))
    
    def delete_directory(self, path: Path, force: bool = False) -> bool:
        """Delete directory and its contents"""
        try:
            if not path.exists():
                self.logger.warning(f"Directory does not exist: {path}")
                return False
            
            if not path.is_dir():
                raise FileSystemError(f"Path is not a directory: {path}", str(path))
            
            if not force and any(path.iterdir()):
                raise FileSystemError(f"Directory not empty (use force=True): {path}", str(path))
            
            shutil.rmtree(path)
            self.logger.debug(f"Directory deleted: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete directory: {e}")
            raise FileSystemError(f"Cannot delete directory: {path}", str(path))
    
    def read_file(self, path: Path, encoding: str = 'utf-8') -> str:
        """Read file content as string"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            self.logger.debug(f"File read: {path} ({len(content)} chars)")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read file: {e}")
            raise FileSystemError(f"Cannot read file: {path}", str(path))
    
    def write_file(self, path: Path, content: str, encoding: str = 'utf-8', overwrite: bool = True) -> bool:
        """Write content to file"""
        try:
            if path.exists() and not overwrite:
                self.logger.warning(f"File already exists: {path}")
                return False
            
            # Ensure directory exists
            self.ensure_directory(path.parent)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.debug(f"File written: {path} ({len(content)} chars)")
            self.logger.file_saved(str(path))
            return True
        except Exception as e:
            self.logger.error(f"Failed to write file: {e}")
            raise FileSystemError(f"Cannot write file: {path}", str(path))
    
    def append_to_file(self, path: Path, content: str, encoding: str = 'utf-8') -> bool:
        """Append content to file"""
        try:
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)
            self.logger.debug(f"Content appended to: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to append to file: {e}")
            raise FileSystemError(f"Cannot append to file: {path}", str(path))
    
    def find_files(self, directory: Path, pattern: str = "*", recursive: bool = True) -> List[Path]:
        """Find files matching pattern in directory"""
        try:
            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))
            
            # Filter to only include files, not directories
            files = [f for f in files if f.is_file()]
            
            self.logger.debug(f"Found {len(files)} files matching '{pattern}' in {directory}")
            return files
        except Exception as e:
            self.logger.error(f"Failed to find files: {e}")
            raise FileSystemError(f"Cannot search directory: {directory}", str(directory))
    
    def get_file_info(self, path: Path) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            if not path.exists():
                raise FileSystemError(f"File does not exist: {path}", str(path))
            
            stat = path.stat()
            return {
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'extension': path.suffix,
                'parent': str(path.parent)
            }
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            raise FileSystemError(f"Cannot get info for: {path}", str(path))
    
    def calculate_file_hash(self, path: Path, algorithm: str = 'md5') -> str:
        """Calculate file hash for integrity checking"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            self.logger.debug(f"File hash ({algorithm}): {path} -> {file_hash}")
            return file_hash
        except Exception as e:
            self.logger.error(f"Failed to calculate file hash: {e}")
            raise FileSystemError(f"Cannot calculate hash for: {path}", str(path))
    
    def backup_file(self, path: Path, backup_dir: Optional[Path] = None) -> Path:
        """Create a backup of the file"""
        try:
            if not path.exists():
                raise FileSystemError(f"File does not exist: {path}", str(path))
            
            if backup_dir is None:
                backup_dir = path.parent / '.backups'
            
            self.ensure_directory(backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{path.stem}_{timestamp}{path.suffix}"
            backup_path = backup_dir / backup_name
            
            self.copy_file(path, backup_path)
            self.logger.info(f"File backed up: {path} -> {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup file: {e}")
            raise FileSystemError(f"Cannot backup file: {path}", str(path))
    
    def cleanup_temp_files(self, temp_dir: Path, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        try:
            if not temp_dir.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            deleted_count = 0
            
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} temporary files from {temp_dir}")
            return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
            raise FileSystemError(f"Cannot cleanup temp directory: {temp_dir}", str(temp_dir))