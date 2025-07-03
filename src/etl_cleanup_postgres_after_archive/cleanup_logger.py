##############################################
# File: cleanup_logger.py
# Purpose: Logs the status of the cleanup process to S3 or local logs
##############################################

import logging
from datetime import datetime
import os


def log_cleanup_summary(config: dict, message: str):
    logger = logging.getLogger(__name__)
    logs_dir = config["directories"]["logs"]
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    log_filename = os.path.join(logs_dir, f"cleanup_log_{timestamp}.log")

    with open(log_filename, "w") as f:
        f.write(f"{timestamp} - {message}\n")

    logger.info(f"📝 Cleanup summary logged to {log_filename}")
