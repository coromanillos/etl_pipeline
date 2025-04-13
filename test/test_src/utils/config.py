##############################################
# Title: Modular Config Script
# Author: Christopher Romanillos
# Description: Modular config script
# Date: 11/23/24
# Version: 1.4
##############################################

import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

from utils.logging import get_logger

# Initialize structured logging with base-case fallback
logger = get_logger(__file__)

def load_config(config_path):
    """Load configuration from a YAML file and initialize logger dynamically."""
    config_path = Path(config_path).resolve()

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info("YAML configuration loaded", path=str(config_path))
        return config

    except FileNotFoundError as e:
        logger.error("Configuration file not found", path=str(config_path), error=str(e))
        raise

    except yaml.YAMLError as e:
        logger.error("YAML parsing error", error=str(e))
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
