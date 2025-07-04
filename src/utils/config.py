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
import logging

logger = logging.getLogger(__name__)

def load_config(config_path):
    config_path = Path(config_path).resolve()

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"YAML configuration loaded: {config_path}")
        return config

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {config_path}", exc_info=True)
        raise

    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}", exc_info=True)
        raise


def load_env_variables(key):
    logger.info("Loading .env file")
    load_dotenv()

    value = os.getenv(key)
    if value is None:
        logger.warning(f"Environment variable not set: {key}")
    else:
        logger.info(f"Environment variable loaded: {key}")

    return value