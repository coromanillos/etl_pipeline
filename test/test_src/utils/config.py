##############################################
# Title: Modular Config Script
# Author: Christopher Romanillos
# Description: Modular config script
# Date: 11/23/24
# Version: 1.1
##############################################

import os
from pathlib import Path
import yaml
from dotenv import load_dotenv
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger()

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
        logger.warn("Environment variable not set", variable=key)
    else:
        logger.info("Environment variable loaded", variable=key)

    return value
