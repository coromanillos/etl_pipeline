##############################################
# Title: S3 Uploader
# Author: Christopher Romanillos
# Description: Uploads Parquet files to S3
# Date: 2025-06-23 | Version: 1.3 (centralized config)
##############################################

import logging
from datetime import datetime
from src.utils.aws_client import get_s3_client

logger = logging.getLogger(__name__)

def generate_s3_key(table_name: str, config: dict, timestamp: str = None) -> str:
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y%m%dT%H%M%SZ")
    path_format = config["s3"].get("path_format", "archive/{table}/dt={date}/{filename}")
    filename = f"{table_name}_{time_str}.parquet"

    return (
        path_format
        .replace("{table}", table_name)
        .replace("{date}", date_str)
        .replace("{filename}", filename)
    )

def upload_file_to_s3(local_file_path: str, config: dict, s3_key: str, bucket_name: str):
    s3_client = get_s3_client(config)
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        logger.info(f"✅ Uploaded {local_file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logger.error(f"❌ Upload failed: {e} | File: {local_file_path}", exc_info=True)
        raise
