from .config_loader import load_config
from .sync_manager import start_sync
import logging
import asyncio
from typing import Dict, List
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def sync_group(group_name: str, folders: List[Path]):
    """Synchronize a single group of folders."""
    try:
        logging.info(f"Starting synchronization for group: {group_name}")
        await start_sync(folders)
    except Exception as e:
        logging.error(f"Error in group {group_name}: {str(e)}")

async def main():
    try:
        folder_groups = load_config()
        tasks = []
        
        for group_name, folders in folder_groups.items():
            logging.info(f"Initializing group {group_name} with folders: {folders}")
            tasks.append(sync_group(group_name, folders))
            
        await asyncio.gather(*tasks)
        
    except Exception as e:
        logging.error(f"Failed to start synchronization: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 