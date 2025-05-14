#############################################################################
# Title: Centralized logging setup
# Author: Christopher Romanillos
# Description: Locate the correct .log file for each specific script
# Date: 05/13/25 | Version: 1.0 
#############################################################################

from utils.logging import get_logger, load_config
import os 

def initialize_pipeline(component_name: str, config_path: str = "../config/config.yaml"):
    """
    Initializes the pipeline by loading configuration and setting up the logger.

    Args:
        component_name (str): Name of the script or pipeline component (e.g., 'extract', 'transform').
        config_path (str): Path to the YAML config file.

    Returns:
        tuple: (config dict, logger instance)
    """
    config = load_config(config_path)
    
    log_file_key = f"{component_name}_log_file"
    log_file = config.get("logging", {}).get(log_file_key)

    if not log_file:
        raise ValueError(f"Missing configuration: logging.{log_file_key}")
    
    logger = get_logger(module_name=component_name, log_file_path=log_file, config_path=config_path)
    logger.info(f"{component_name.capitalize()} pipeline initialized.")
    
    print(f"[DEBUG] Log file path resolved to: {os.path.abspath(log_file)}")
    return config, logger
