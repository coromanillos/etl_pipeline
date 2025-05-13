#############################################################################
# Title: Centralized logging setup
# Author: Christopher Romanillos
# Description: Locate the correct .log file for each specific script
# Date: 05/13/25 | Version: 1.0 
#############################################################################

from utils.logging import get_logger
from utils.utils import load_config
import os 

def initialize_pipeline(component_name: str, config_path: str = "../config/config.yaml"):
    config = load_config(config_path)
    
    log_file_key = f"{component_name}_log_file"
    log_file = config.get("logging", {}).get(log_file_key)

    if not log_file:
        raise ValueError(f"Missing configuration: logging.{log_file_key}")
    
    logger = get_logger(component_name, log_file)
    logger.info(f"{component_name.capitalize()} pipeline initialized.")
    
    print(f"[DEBUG] Log file path resolved to: {os.path.abspath(log_file)}")
    return config, logger
