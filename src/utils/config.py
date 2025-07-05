##############################################
# Title: Config Utility Module
# Author: Christopher Romanillos
# Description: Loads YAML config (non-secrets)
# Date: 2025-07-04
# Version: 3.0 (Production-ready, no .env usage)
##############################################

import os
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "/opt/airflow/config/config.yaml"

def load_config(config_path: str = None) -> dict:
    config_path = Path(config_path or DEFAULT_CONFIG_PATH).resolve()

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        logger.info(f"✅ Loaded YAML config from: {config_path}")
        return config

    except FileNotFoundError:
        logger.error(f"❌ Config file not found: {config_path}", exc_info=True)
        raise

    except yaml.YAMLError as e:
        logger.error(f"❌ YAML parsing error: {e}", exc_info=True)
        raise

def get_env_var(key: str, required: bool = True) -> str:
    value = os.getenv(key)

    if value is None:
        msg = f"⚠️ Missing required environment variable: {key}"
        if required:
            logger.error(msg)
            raise EnvironmentError(msg)
        else:
            logger.warning(msg)
    else:
        logger.debug(f"🔑 Loaded env var: {key}")

    return value