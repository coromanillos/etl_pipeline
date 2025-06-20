import boto3
import os

def upload_to_s3(file_path: str, bucket: str, s3_key: str, logger):
    s3 = boto3.client("s3")
    logger.info(f"Uploading {file_path} to s3://{bucket}/{s3_key}")
    
    s3.upload_file(file_path, bucket, s3_key)
    logger.info("Upload complete.")
