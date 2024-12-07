from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import List
import time
import asyncio
from .file_handler import sync_file_operation
import logging

logger = logging.getLogger(__name__)

class FolderSyncHandler(FileSystemEventHandler):
    def __init__(self, folders: List[Path], src_root: Path):
        self.folders = folders
        self.src_root = src_root
        super().__init__()

    def handle_event(self, event, operation: str):
        """Generic event handler with synchronization protection."""
        try:
            if event.is_directory:
                return

            src_path = Path(event.src_path)
            
            # Skip if path is already being processed
            sync_file_operation(
                src_path,
                self.folders,
                operation,
                self.src_root
            )

        except Exception as e:
            logger.error(f"Error handling {operation} event: {str(e)}")

    def on_created(self, event):
        self.handle_event(event, "created")

    def on_modified(self, event):
        self.handle_event(event, "modified")

    def on_deleted(self, event):
        self.handle_event(event, "deleted")

async def start_sync(folders: List[Path]) -> None:
    """Start the folder synchronization process."""
    observer = Observer()
    
    try:
        for folder in folders:
            handler = FolderSyncHandler(folders, folder)
            observer.schedule(handler, str(folder), recursive=True)
            logger.info(f"Started monitoring: {folder}")
            
        observer.start()
        logger.info("Observer started")
        
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in sync process: {str(e)}")
        raise
    finally:
        observer.stop()
        observer.join()
        logger.info("Synchronization stopped") 