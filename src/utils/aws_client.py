##############################################
# Title: AWS Client
# Author: Christopher Romanillos
# Description: Isolate logic for initializing
# AWS client
# Date: 2025-07-05
##############################################

import boto3
import logging

logger = logging.getLogger(__name__)

def get_s3_client(config: dict, client_factory=boto3.client):
    try:
        if config.get("use_localstack"):
            return client_factory(
                "s3",
                region_name=config["s3"]["region"],
                endpoint_url=config["s3"].get("endpoint_url", "http://localhost:4566"),
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
        else:
            return client_factory("s3", region_name=config["s3"]["region"])
    except Exception as e:
        logger.error(f"❌ Failed to create S3 client: {e}", exc_info=True)
        raise
