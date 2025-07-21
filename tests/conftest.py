# conftest.py

import os
import yaml
import pytest
import logging
from src.utils.aws_client import get_s3_client
from src.utils.db_client import get_postgres_connection
from src.utils.redshift_client import get_redshift_connection
from src.utils.postgres_cleaner import drop_all_tables, vacuum_postgres
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# -----------------------------
# Build connection strings dynamically
# -----------------------------

def build_postgres_conn_string(cfg):
    pg = cfg["postgres_loader"]
    return f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"


def build_redshift_conn_string(cfg):
    rs = cfg["redshift"]
    return f"postgresql://{rs['user']}:{rs['password']}@{rs['host']}:{rs['port']}/{rs['db']}"


# -----------------------------
# Load Different Test Configs (With Expanded .env)
# -----------------------------

@pytest.fixture(scope="session")
def test_rest_config():
    with open("config/test/test_rest_config.yaml") as f:
        config = yaml.safe_load(f)
    return expand_env_vars(config)


@pytest.fixture(scope="session")
def test_postgres_config():
    with open("config/test/test_postgres_config.yaml") as f:
        config = yaml.safe_load(f)
    return expand_env_vars(config)


@pytest.fixture(scope="session")
def test_redshift_config():
    with open("config/test/test_redshift_config.yaml") as f:
        config = yaml.safe_load(f)
    return expand_env_vars(config)


# -----------------------------
# PostgreSQL Fixtures
# -----------------------------

@pytest.fixture(scope="session", autouse=True)
def ensure_test_postgres_schema(test_postgres_config):
    """
    Ensure the 'intraday_data' table exists before tests run in 'etl' schema.
    """
    connection_string = build_postgres_conn_string(test_postgres_config)
    schema = test_postgres_config["postgres_loader"]["schema"]

    create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema};"

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {schema}.intraday_data (
        id BIGSERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL UNIQUE,
        open DOUBLE PRECISION NOT NULL,
        high DOUBLE PRECISION NOT NULL,
        low DOUBLE PRECISION NOT NULL,
        close DOUBLE PRECISION NOT NULL,
        volume BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """

    with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
        with conn.cursor() as cur:
            cur.execute(create_schema_query)
            cur.execute(create_table_query)
        conn.commit()


@pytest.fixture
def clear_postgres_table():
    def _clear(config, table_name):
        connection_string = build_postgres_conn_string(config)
        schema = config["postgres_loader"]["schema"]
        with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {schema}.{table_name};")
            conn.commit()
    return _clear


@pytest.fixture
def drop_all_postgres_tables():
    """Drop all tables within a PostgreSQL schema."""
    def _drop(config, logger):
        # Build connection string dynamically
        connection_string = build_postgres_conn_string(config)
        config_with_conn = {"postgres_loader": {"connection_string": connection_string}}
        drop_all_tables(config_with_conn, logger)
    return _drop


@pytest.fixture
def vacuum_postgres_fixture():
    """Run VACUUM FULL on PostgreSQL."""
    def _vacuum(config, logger):
        connection_string = build_postgres_conn_string(config)
        config_with_conn = {"postgres_loader": {"connection_string": connection_string}}
        vacuum_postgres(config_with_conn, logger)
    return _vacuum


# -----------------------------
# Redshift Fixtures
# -----------------------------

@pytest.fixture
def clear_redshift_table():
    """Drop a Redshift table before tests."""
    def _clear(config, table_name):
        connection_string = build_redshift_conn_string(config)
        schema = config["redshift"]["schema"]
        query = f"DROP TABLE IF EXISTS {schema}.{table_name};"
        with get_redshift_connection({"redshift": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
    return _clear


# -----------------------------
# S3 Fixtures
# -----------------------------

@pytest.fixture
def delete_s3_key():
    """Delete an S3 object after tests."""
    def _delete(config, key):
        bucket = config["s3"]["archive_bucket"]
        s3_client = get_s3_client(config)
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except Exception:
            logging.warning(f"⚠️ Could not delete S3 key {key} from bucket {bucket}")
    return _delete


# -----------------------------
# Pytest Markers
# -----------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "end_to_end: mark a test as a full end-to-end pipeline test")
