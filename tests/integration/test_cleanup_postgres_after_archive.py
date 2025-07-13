# tests/integration/test_postgres_cleanup.py

import os
import pytest
import logging
from src.table_cleaner import drop_all_tables
from src.vacuum_executor import vacuum_postgres
from src.cleanup_logger import log_cleanup_summary

@pytest.mark.integration
def test_postgres_cleanup(test_config, drop_all_tables, vacuum_postgres, tmp_path):
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler())

    # STEP 1: Ensure logs directory exists
    logs_dir = tmp_path / "logs"
    os.makedirs(logs_dir, exist_ok=True)
    test_config["directories"]["logs"] = str(logs_dir)

    # STEP 2: Drop all tables
    drop_all_tables(test_config, logger)

    # STEP 3: Perform VACUUM FULL
    vacuum_postgres(test_config, logger)

    # STEP 4: Log cleanup summary
    log_message = "Postgres cleanup pipeline completed successfully."
    log_cleanup_summary(test_config, logger, log_message)

    # STEP 5: Validate log file exists and contains expected message
    assert os.path.isdir(logs_dir), f"Logs directory {logs_dir} should exist."

    log_files = os.listdir(logs_dir)
    assert any(f.startswith("cleanup_log_") and f.endswith(".log") for f in log_files), "No cleanup log files found."

    log_file_path = os.path.join(logs_dir, log_files[0])
    content = open(log_file_path).read()
    assert log_message in content, "Cleanup message not found in log file."
