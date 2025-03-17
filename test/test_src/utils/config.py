##############################################
# Title: Modular Config Script
# Author: Christopher Romanillos
# Description: modular config script
# Date: 11/23/24
# Version: 1.0
##############################################
import yaml
import logging
import sys
from dotenv import load_dotenv
from pathlib import Path
import os # Still needed for enviornment variable loading, pathlib does not replace it...


# Configure logging to send logs to stdout
logging.basicConfig(
    level=logging.INFO,  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  # Ensure logs go to stdout for Docker
)

def load_config(config_path):
    """Load configuration from a YAML file."""
    config_path = Path(config_path).resolve()  # Ensure the config path is absolute
    logging.info(f"Loading configuration from {config_path}")

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logging.info("Configuration loaded successfully.")
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise

def load_env_variables(key):
    """Load environment variables."""
    logging.info("Loading environment variables from .env file")
    load_dotenv()

    value = os.getenv(key)
    if value is None:
        logging.warning(f"Environment variable '{key}' is not set.")
    else:
        logging.info(f"Environment variable '{key}' loaded successfully.")
    
    return value