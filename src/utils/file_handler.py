##############################################
# Title: Modular File Handling Script
# Author: Christopher Romanillos
# Description: Modular utils script with Docker logging support.
# Date: 2025-05-18
# Version: 1.6 (refactored for consistent return values and modern logging)
##############################################

import json
from datetime import datetime
from pathlib import Path
from utils.logging import get_logger

logger = get_logger(__file__)

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

    Returns:
        str or None: The path to the saved file if successful, otherwise None.
    """
    try:
        processed_data_path = Path(processed_data_dir)
        processed_data_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = processed_data_path / f"processed_data_{timestamp}.json"

        with open(file_name, 'w') as file:
            json.dump(data, file, default=str)

        logger.info("Processed data saved", file=str(file_name))
        return str(file_name)
    except Exception as e:
        logger.error("Error saving processed data", directory=processed_data_dir, error=str(e))
        return None

def save_raw_data(data, raw_data_dir):
    """
    Save raw data as a JSON file with a timestamped filename.

    Args:
        data (dict or list): The raw data to save.
        raw_data_dir (str): The directory where the file should be saved.

    Returns:
        str or None: The path to the saved file if successful, otherwise None.
    """
    try:
        raw_data_path = Path(raw_data_dir)
        raw_data_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = raw_data_path / f"raw_data_{timestamp}.json"

        with open(file_name, 'w') as file:
            json.dump(data, file, default=str)

        logger.info("Raw data saved", file=str(file_name))
        return str(file_name)
    except Exception as e:
        logger.error("Error saving raw data", directory=raw_data_dir, error=str(e))
        return None