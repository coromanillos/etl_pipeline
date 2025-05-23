#############################################################################
# Title: Centralized logging setup (modernized)
# Author: Christopher Romanillos, Copilot
# Description: Loads config, sets up structured logger for a pipeline component
# Date: 2025-05-18 | Version: 2.0 
#############################################################################

from utils.logging import get_logger, load_config

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
    logger = get_logger(module_name=component_name, config_path=config_path)
    logger.info(f"{component_name.capitalize()} pipeline initialized.")
    return config, logger