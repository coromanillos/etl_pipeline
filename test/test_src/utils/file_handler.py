##############################################
# Title: Modular File Handling Script
# Author: Christopher Romanillos
# Description: Modular utils script with Docker logging support.
# Date: 12/01/24
# Version: 1.3
##############################################

import json
from datetime import datetime
from pathlib import Path
from utils.logging import get_logger  # Centralized structured logger

# Bind structured logger to this module
logger = get_logger("file_handler")

def get_latest_file(directory: str, pattern: str = "*.json") -> Path:
    """
    Get the most recent file in a directory based on a pattern.

    Args:
        directory (str): The path to the directory to search.
        pattern (str): The file pattern to match (default is '*.json').

    Returns:
        Path: The most recently created or modified file that matches the pattern.

    Raises:
        FileNotFoundError: If no matching files are found.
        Exception: For other unexpected errors.
    """
    try:
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{directory} is not a valid directory.")

        files = list(dir_path.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No files matching pattern '{pattern}' found in {directory}.")

        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        logger.info("Latest file found", file=str(latest_file))
        return latest_file
    except Exception as e:
        logger.error("Error locating the latest file", directory=directory, pattern=pattern, error=str(e))
        raise

def save_processed_data(data, processed_data_dir):
    """
    Save processed data as a JSON file with a timestamped filename.

    Args:
        data (dict or list): The processed data to save.
        processed_data_dir (str): The directory where the file should be saved.

    Raises:
        Exception: If there's an error during file writing.
    """
    try:
        processed_data_path = Path(processed_data_dir)
        processed_data_path.mkdir(parents=True, exist_ok=True)

        file_name = processed_data_path / f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(file_name, 'w') as file:
            json.dump(data, file, default=str)

        logger.info("Processed data saved", file=str(file_name))
    except Exception as e:
        logger.error("Error saving processed data", directory=processed_data_dir, error=str(e))
        raise
