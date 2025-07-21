# tests/integration/conftest.py

import pytest
import yaml
from src.utils.config import expand_env_vars
from src.utils.db_client import get_postgres_connection
from src.utils.postgres_cleaner import drop_all_tables, vacuum_postgres


@pytest.fixture(scope="session")
def test_postgres_config():
    with open("config/test/test_postgres_config.yaml") as f:
        return expand_env_vars(yaml.safe_load(f))


@pytest.fixture(scope="session")
def test_redshift_config():
    with open("config/test/test_redshift_config.yaml") as f:
        return expand_env_vars(yaml.safe_load(f))


@pytest.fixture(scope="session", autouse=True)
def ensure_test_postgres_schema(test_postgres_config):
    """Ensure schema and table exist for integration testing."""
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
    with get_postgres_connection(test_postgres_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_schema_query)
            cur.execute(create_table_query)
        conn.commit()


@pytest.fixture
def clear_postgres_table():
    """Clear all rows from a specified Postgres table."""
    def _clear(config, table_name):
        schema = config["postgres_loader"]["schema"]
        with get_postgres_connection(config) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {schema}.{table_name};")
            conn.commit()
    return _clear


@pytest.fixture
def clear_redshift_table():
    """Drop a Redshift table if it exists."""
    from src.utils.redshift_client import get_redshift_connection

    def _clear(config, table_name):
        connection_string = (
            f"postgresql://{config['redshift']['user']}:"
            f"{config['redshift']['password']}@"
            f"{config['redshift']['host']}:"
            f"{config['redshift']['port']}/"
            f"{config['redshift']['db']}"
        )
        schema = config["redshift"]["schema"]
        drop_query = f"DROP TABLE IF EXISTS {schema}.{table_name};"
        with get_redshift_connection({"redshift": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute(drop_query)
            conn.commit()
    return _clear


@pytest.fixture
def delete_s3_key():
    """Delete a file from S3 after test."""
    from src.utils.aws_client import get_s3_client

    def _delete(config, key):
        bucket = config["s3"]["archive_bucket"]
        s3_client = get_s3_client(config)
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except Exception:
            pass  # Silence expected "key not found" cleanup errors
    return _delete
