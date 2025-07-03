##############################################
# File: s3_uploader.py
# Author: Christopher Romanillos
# Description: Uploads Parquet files to S3
# Date: 06/23/25
##############################################

import logging
import boto3
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_s3_key(table_name: str, config: dict, timestamp: str = None) -> str:
    from datetime import datetime

    # Use a consistent run timestamp if not passed
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y%m%dT%H%M%SZ")

    path_format = config["s3"].get("path_format", "archive/{table}/dt={date}/{filename}")
    filename = f"{table_name}_{time_str}.parquet"

    s3_key = (
        path_format
        .replace("{table}", table_name)
        .replace("{date}", date_str)
        .replace("{filename}", filename)
    )

    return s3_key

def upload_file_to_s3(local_file_path: str, config: dict, s3_key: str) -> None:
    s3_bucket = config["s3"]["bucket"]
    s3_region = config["s3"]["region"]
    s3_client = boto3.client("s3", region_name=s3_region)
    try:
        s3_client.upload_file(local_file_path, s3_bucket, s3_key)
        logger.info(f"✅ Uploaded {local_file_path} to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        logger.error(f"❌ Upload failed: {e} | File: {local_file_path}", exc_info=True)
        raise
