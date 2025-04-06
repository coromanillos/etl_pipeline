##############################################
# Title: Modular Config Script
# Author: Christopher Romanillos
# Description: Modular config script
# Date: 11/23/24
# Version: 1.2
##############################################

import os
from pathlib import Path
import yaml
from dotenv import load_dotenv
from utils.logging import get_logger  # Import from your centralized logger module

logger = get_logger("config")  # Bind context to this module

def load_config(config_path):
    """Load configuration from a YAML file."""
    config_path = Path(config_path).resolve()
    logger.info("Loading YAML configuration", path=str(config_path))

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
            return config
    except FileNotFoundError:
        logger.error("Configuration file not found", path=str(config_path))
        raise
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML", error=str(e))
        raise

def load_env_variables(key):
    """Load environment variable from .env file."""
    logger.info("Loading .env file")
    load_dotenv()

    value = os.getenv(key)
    if value is None:
        logger.warning("Environment variable not set", variable=key)
    else:
        logger.info("Environment variable loaded", variable=key)

    return value
