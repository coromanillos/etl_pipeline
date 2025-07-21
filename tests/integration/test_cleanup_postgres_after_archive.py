# tests/integration/test_cleanup_postgres_after_archive.py

import os
import pytest
from src.utils.postgres_cleaner import drop_all_tables, vacuum_postgres
from src.etl_cleanup_postgres_after_archive.cleanup_logger import log_cleanup_summary


@pytest.mark.integration
def test_postgres_cleanup(test_postgres_config, tmp_path):
    logs_dir = tmp_path / "logs"
    os.makedirs(logs_dir, exist_ok=True)
    test_postgres_config["directories"]["logs"] = str(logs_dir)

    drop_all_tables(test_postgres_config)
    vacuum_postgres(test_postgres_config)

    log_message = "Postgres cleanup pipeline completed successfully."
    log_cleanup_summary(test_postgres_config, log_message)

    assert os.path.isdir(logs_dir), f"Logs directory {logs_dir} should exist."

    log_files = [f for f in os.listdir(logs_dir) if f.startswith("cleanup_log_") and f.endswith(".log")]
    assert log_files, "No cleanup log files found."

    log_file_path = os.path.join(logs_dir, log_files[0])
    with open(log_file_path) as f:
        content = f.read()
    assert log_message in content, "Cleanup message not found in log file."
