##############################################
# Title: Modular Config Script
# Author: Christopher Romanillos
# Description: Modular config script
# Date: 11/23/24
# Version: 1.3
##############################################

import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Delay logger creation until after config is loaded
logger = None

def load_config(config_path):
    """Load configuration from a YAML file and initialize logger dynamically."""
    global logger
    config_path = Path(config_path).resolve()

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        # Use basic logging temporarily if full logger hasn't been configured yet
        import logging
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        import logging
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"YAML parsing error: {e}")
        raise

    # Set up dynamic logger now that config is available
    from utils.logging import get_logger, setup_logging
    setup_logging()  # Ensures logger uses the dynamic level
    logger = get_logger("config")

    logger.info("YAML configuration loaded", path=str(config_path))
    return config

def load_env_variables(key):
    """Load environment variable from .env file."""
    if not logger:
        from utils.logging import get_logger
        global logger
        logger = get_logger("config")

    logger.info("Loading .env file")
    load_dotenv()

    value = os.getenv(key)
    if value is None:
        logger.warning("Environment variable not set", variable=key)
    else:
        logger.info("Environment variable loaded", variable=key)

    return value
