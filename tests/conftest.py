# conftest
import os
import yaml
import pytest
import logging
from src.utils.aws_client import get_s3_client
from src.utils.db_client import get_postgres_connection
from src.utils.redshift_client import get_redshift_connection
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# -----------------------------
# Helper Function to Expand Env Vars
# -----------------------------

def expand_env_vars(value):
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env_vars(i) for i in value]
    return value


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

@pytest.fixture
def clear_postgres_table():
    def _clear(config, table_name):
        connection_string = config["postgres_loader"]["connection_string"]
        with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {table_name};")
            conn.commit()
    return _clear


@pytest.fixture
def drop_all_postgres_tables():
    """Drop all tables within a PostgreSQL schema."""
    def _drop(config, logger):
        connection_string = config["postgres_loader"]["connection_string"]
        schema = config["postgres_loader"]["schema"]

        query = f"""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = '{schema}') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS {schema}.' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """
        with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
                logger.info(f"✅ Dropped all tables in schema '{schema}'.")
    return _drop


@pytest.fixture
def vacuum_postgres():
    """Run VACUUM FULL on PostgreSQL."""
    def _vacuum(config, logger):
        connection_string = config["postgres_loader"]["connection_string"]
        with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute("VACUUM FULL;")
                conn.commit()
                logger.info("✅ VACUUM FULL executed successfully.")
    return _vacuum


# -----------------------------
# Redshift Fixtures
# -----------------------------

@pytest.fixture
def clear_redshift_table():
    """Drop a Redshift table before tests."""
    def _clear(config, table_name):
        connection_string = config["redshift"]["connection_string"]
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
