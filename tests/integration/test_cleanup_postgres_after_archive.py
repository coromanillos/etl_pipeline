# tests/integration/test_cleanup_postgres_after_archive.py

import os
import pytest
from src.utils.postgres_cleaner import drop_all_tables, vacuum_postgres
from src.etl_cleanup_postgres_after_archive.cleanup_logger import log_cleanup_summary


@pytest.mark.integration
def test_postgres_cleanup(test_postgres_config, tmp_path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    test_postgres_config["directories"]["logs"] = str(logs_dir)

    drop_all_tables(test_postgres_config)
    vacuum_postgres(test_postgres_config)

    log_message = "Postgres cleanup pipeline completed successfully."
    log_cleanup_summary(test_postgres_config, log_message)

    log_files = list(logs_dir.glob("cleanup_log_*.log"))
    assert log_files, "No cleanup log files found."

    log_file_path = log_files[0]
    content = log_file_path.read_text()
    assert log_message in content, "Cleanup message not found in log file."
