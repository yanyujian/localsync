from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import List
import time
from .file_handler import sync_file_operation
import logging
import threading

logger = logging.getLogger(__name__)

class FolderSyncHandler(FileSystemEventHandler):
    _lock = threading.Lock()
    _processing = set()

    def __init__(self, folders: List[Path], src_root: Path):
        self.folders = folders
        self.src_root = src_root
        super().__init__()

    def _is_being_processed(self, path: str) -> bool:
        """Check if a path is currently being processed."""
        with self._lock:
            if path in self._processing:
                return True
            self._processing.add(path)
            return False

    def _finish_processing(self, path: str) -> None:
        """Mark a path as done processing."""
        with self._lock:
            self._processing.discard(path)

    def handle_event(self, event, operation: str):
        """Generic event handler with synchronization protection."""
        try:
            if event.is_directory:
                return

            src_path = Path(event.src_path)
            
            # Skip if path is already being processed
            if self._is_being_processed(str(src_path)):
                return

            try:
                sync_file_operation(
                    src_path,
                    self.folders,
                    operation,
                    self.src_root
                )
            finally:
                # Always mark as done processing
                self._finish_processing(str(src_path))

        except Exception as e:
            logger.error(f"Error handling {operation} event: {str(e)}")

    def on_created(self, event):
        self.handle_event(event, "created")

    def on_modified(self, event):
        self.handle_event(event, "modified")

    def on_deleted(self, event):
        self.handle_event(event, "deleted")

def start_sync(folders: List[Path]) -> None:
    """Start the folder synchronization process."""
    observers = []
    
    try:
        for folder in folders:
            observer = Observer()
            handler = FolderSyncHandler(folders, folder)
            observer.schedule(handler, str(folder), recursive=True)
            observer.start()
            observers.append(observer)
            logger.info(f"Started monitoring: {folder}")

        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
            observer.join()
        logger.info("Synchronization stopped") 