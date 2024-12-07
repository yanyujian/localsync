from pathlib import Path
from typing import List, Dict
import yaml
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml") -> Dict[str, List[Path]]:
    """Load folder paths from configuration file."""
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        if not config:
            raise ValueError("Config file is empty")
            
        result = {}
        
        # Handle single group configuration
        if "folders" in config:
            folders = [Path(folder).resolve() for folder in config["folders"]]
            result["default"] = folders
            
        # Handle multiple groups configuration
        if "folder_groups" in config:
            for group_name, folders in config["folder_groups"].items():
                result[group_name] = [Path(folder).resolve() for folder in folders]
                
        if not result:
            raise ValueError("No valid folder configuration found")
            
        # Validate all folders
        for group_folders in result.values():
            for folder in group_folders:
                if not folder.exists():
                    folder.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created folder: {folder}")
                    
        return result
    
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML format: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}") 