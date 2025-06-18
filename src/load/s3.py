import boto3
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def upload_file_to_s3(file_path: Path, s3_key: str):
    bucket = os.getenv("S3_BUCKET")
    region = os.getenv("S3_REGION")

    s3 = boto3.client("s3", region_name=region)
    s3.upload_file(str(file_path), bucket, s3_key)
