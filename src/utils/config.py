##############################################
# Title: Config utility script
# Author: Christopher Romanillos
# Description: Loads YAML and environment configs 
# Date: 2025-07-04
# Version: 2.0 (Production-ready)
##############################################

import os
import logging
from pathlib import Path
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Default location for config.yaml inside Dockerized Airflow
DEFAULT_CONFIG_PATH = "/opt/airflow/config/config.yaml"

def load_config(config_path: str = None) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path (str, optional): Path to config file. Defaults to internal Docker path.

    Returns:
        dict: Parsed configuration data.
    """
    config_path = Path(config_path or DEFAULT_CONFIG_PATH).resolve()

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        logger.info(f"✅ YAML configuration loaded from: {config_path}")
        return config

    except FileNotFoundError as e:
        logger.error(f"❌ Configuration file not found: {config_path}", exc_info=True)
        raise

    except yaml.YAMLError as e:
        logger.error(f"❌ YAML parsing error: {e}", exc_info=True)
        raise

def load_env_variable(key: str, use_dotenv: bool = False) -> str:
    """
    Load an environment variable with optional .env support.

    Args:
        key (str): Environment variable name.
        use_dotenv (bool): Whether to load from .env (for local dev).

    Returns:
        str: Value of the environment variable (or None if not found).
    """
    if use_dotenv:
        logger.info("📦 Loading environment variables from .env file")
        load_dotenv()

    value = os.getenv(key)

    if value is None:
        logger.warning(f"⚠️ Environment variable not set: {key}")
    else:
        logger.info(f"🔑 Loaded environment variable: {key}")

    return value
