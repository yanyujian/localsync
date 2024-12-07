import pytest
from pathlib import Path
from src.config_loader import load_config
from src.file_handler import sync_file_operation
import tempfile
import shutil
import yaml

@pytest.fixture
def temp_folders():
    with tempfile.TemporaryDirectory() as dir1, \
         tempfile.TemporaryDirectory() as dir2:
        yield [Path(dir1), Path(dir2)]

def test_sync_file_creation(temp_folders):
    # Create a test file in the first folder
    test_file = temp_folders[0] / "test.txt"
    test_file.write_text("test content")
    
    # Sync the creation
    sync_file_operation(test_file, temp_folders, "created", temp_folders[0])
    
    # Verify file exists in second folder
    synced_file = temp_folders[1] / "test.txt"
    assert synced_file.exists()
    assert synced_file.read_text() == "test content" 