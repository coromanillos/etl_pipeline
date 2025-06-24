##############################################
# File: s3_uploader.py
# Author: Christopher Romanillos
# Description: Uploads Parquet files to S3
#              using env + config settings.
# Date: 06/23/25
##############################################

import os
import boto3
import yaml
import logging
from dotenv import load_dotenv
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Optional: configure log formatting (for local testing)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Load environment variables
load_dotenv()

# Load config.yaml
def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Pull config values
S3_BUCKET = os.getenv("S3_BUCKET") or CONFIG["s3"]["bucket"]
S3_REGION = os.getenv("S3_REGION") or CONFIG["s3"]["region"]
PATH_FORMAT = CONFIG["s3"].get("path_format", "archive/{date}/{filename}")

# Create an S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)


def generate_s3_key(table_name: str, timestamp: str = None) -> str:
    """
    Creates a dynamic S3 object key/path based on table name and timestamp.
    """
    if not timestamp:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
    
    filename = f"{table_name}_{timestamp}.parquet"
    s3_key = PATH_FORMAT.replace("{date}", timestamp).replace("{filename}", filename)

    return s3_key


def upload_file_to_s3(local_file_path: str, s3_key: str) -> None:
    """
    Uploads a local file to the configured S3 bucket with the given object key.
    Logs success or failure.
    """
    try:
        s3_client.upload_file(local_file_path, S3_BUCKET, s3_key)
        logger.info(f"✅ Uploaded {local_file_path} to s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        logger.error(f"❌ Failed to upload {local_file_path} to s3://{S3_BUCKET}/{s3_key}: {e}")
        raise
