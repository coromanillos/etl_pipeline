# tests/integration/conftest.py

import os
import pytest
import yaml

@pytest.fixture(scope="session")
def test_config(request):
    """
    Dynamically load the appropriate test config file based on test marker or default to REST config.
    """
    marker = request.node.get_closest_marker("config_file")
    config_file = marker.args[0] if marker else "config/test/test_rest_config.yaml"
    
    with open(config_file) as f:
        return yaml.safe_load(f)

@pytest.fixture
def clear_table():
    """
    Returns a reusable DB table cleaner function.
    Usage: clear_table(config, "table_name")
    """
    from src.utils.db_client import get_postgres_connection

    def _clear_table(config, table_name):
        conn = get_postgres_connection(config)
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {table_name};")
            conn.commit()

    return _clear_table
