# tests/integration/test_postgres_after_cleanup.py

import os
import pytest
import logging

@pytest.mark.integration
def test_postgres_cleanup(test_postgres_config, drop_all_postgres_tables, vacuum_postgres, tmp_path):
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler())

    logs_dir = tmp_path / "logs"
    os.makedirs(logs_dir, exist_ok=True)
    test_postgres_config["directories"]["logs"] = str(logs_dir)

    drop_all_postgres_tables(test_postgres_config, logger)
    vacuum_postgres(test_postgres_config, logger)

    log_message = "Postgres cleanup pipeline completed successfully."
    from src.etl_cleanup_postgres_after_archive.cleanup_logger import log_cleanup_summary
    log_cleanup_summary(test_postgres_config, logger, log_message)

    assert os.path.isdir(logs_dir), f"Logs directory {logs_dir} should exist."

    log_files = [f for f in os.listdir(logs_dir) if f.startswith("cleanup_log_") and f.endswith(".log")]
    assert log_files, "No cleanup log files found."

    log_file_path = os.path.join(logs_dir, log_files[0])
    with open(log_file_path) as f:
        content = f.read()
    assert log_message in content, "Cleanup message not found in log file."
