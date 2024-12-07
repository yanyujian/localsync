from pathlib import Path
import shutil
from typing import List
import logging
import os
import time
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_file_hash(file_path: Path) -> str:
    """Calculate file hash to compare content."""
    if not file_path.exists() or not file_path.is_file():
        return ""
    
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""

def is_file_in_use(file_path: Path) -> bool:
    """Check if a file is currently being used/edited."""
    if not file_path.exists():
        return False
    try:
        # Try to open the file in read-write mode
        with open(file_path, 'r+b') as f:
            # Try to acquire an exclusive lock
            if os.name == 'nt':  # Windows
                import msvcrt
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except IOError:
                    return True
            else:  # Unix-based systems
                import fcntl
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except IOError:
                    return True
        return False
    except (IOError, PermissionError):
        return True

def get_file_info(path: Path) -> dict:
    """Get file information including modification time, size and hash."""
    if not path.exists():
        return {'mtime': datetime.min, 'size': 0, 'hash': ''}
    
    stat = path.stat()
    return {
        'mtime': datetime.fromtimestamp(stat.st_mtime),
        'size': stat.st_size,
        'hash': get_file_hash(path)
    }

def should_sync_files(src_path: Path, target_path: Path) -> bool:
    """Determine if files should be synchronized based on content and timestamps."""
    if not src_path.exists():
        return False
        
    src_info = get_file_info(src_path)
    target_info = get_file_info(target_path)
    
    # If hashes are different, the newer file should win
    if src_info['hash'] != target_info['hash']:
        # If target is newer and has different content, don't sync
        if target_info['mtime'] > src_info['mtime']:
            logger.info(f"Target file is newer with different content: {target_path}")
            return False
            
        # If source is newer or same time but different content, do sync
        return True
        
    # If hashes are same, files are identical - no need to sync
    return False

def get_delete_filename(path: Path) -> Path:
    """Generate a backup filename for deleted files."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return path.parent / f"{path.name}.deleted.at{timestamp}"

def safe_delete(path: Path) -> None:
    """Safely 'delete' a file by renaming it with a timestamp."""
    if not path.exists():
        return
        
    try:
        new_path = get_delete_filename(path)
        path.rename(new_path)
        logger.info(f"Safely deleted {path} -> {new_path}")
    except Exception as e:
        logger.error(f"Failed to safely delete {path}: {str(e)}")
        raise

def sync_file_operation(
    src_path: Path,
    folders: List[Path],
    operation: str,
    src_root: Path
) -> None:
    """Synchronize file operations across folders."""
    try:
        # Calculate relative path
        rel_path = src_path.relative_to(src_root)
        
        for folder in folders:
            if folder == src_root:
                continue
                
            target_path = folder / rel_path
            
            if operation == "created" or operation == "modified":
                # Skip if source file is being edited
                if is_file_in_use(src_path):
                    logger.info(f"Skipping sync as source file is being edited: {src_path}")
                    return

                # Skip if target file is being edited
                if target_path.exists() and is_file_in_use(target_path):
                    logger.info(f"Skipping sync as target file is being edited: {target_path}")
                    return

                # For files, check content and timestamps
                if src_path.is_file():
                    if not should_sync_files(src_path, target_path):
                        return
                        
                    # Add a small delay to ensure file is completely written
                    time.sleep(0.1)
                    
                    # Double check content hasn't changed during delay
                    if not should_sync_files(src_path, target_path):
                        return
                        
                    # Proceed with copy
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, target_path)
                    logger.info(f"Synchronized: {target_path}")
                    
                elif src_path.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                    
            elif operation == "deleted":
                if target_path.exists():
                    # Skip if target file is being edited
                    if is_file_in_use(target_path):
                        logger.info(f"Skipping deletion as file is being edited: {target_path}")
                        return
                        
                    if target_path.is_file():
                        # Instead of deleting, rename with timestamp
                        safe_delete(target_path)
                    elif target_path.is_dir():
                        # For directories, rename the entire directory
                        safe_delete(target_path)
                        
            logger.info(f"{operation.capitalize()}: {target_path}")
            
    except Exception as e:
        logger.error(f"Failed to sync {operation} for {src_path}: {str(e)}")