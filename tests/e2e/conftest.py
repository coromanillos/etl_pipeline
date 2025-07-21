# tsets/e2e/conftest.py

import pytest
import yaml
import logging

from src.utils.config import expand_env_vars
from src.utils.db_client import get_postgres_connection
from src.utils.redshift_client import get_redshift_connection
from src.utils.aws_client import get_s3_client


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def e2e_config():
    with open("config/test/test_rest_config.yaml") as f:
        return expand_env_vars(yaml.safe_load(f))


@pytest.fixture
def clear_postgres_table():
    """Clears a Postgres table for E2E tests."""
    def _clear(config, table_name):
        schema = config["postgres_loader"]["schema"]
        with get_postgres_connection(config) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {schema}.{table_name};")
            conn.commit()
    return _clear


@pytest.fixture
def clear_redshift_table():
    """Drops a Redshift table for E2E tests."""
    def _clear(config, table_name):
        connection_string = config["redshift"]["connection_string"]
        schema = config["redshift"]["schema"]
        query = f"DROP TABLE IF EXISTS {schema}.{table_name};"
        with get_redshift_connection({"redshift": {"connection_string": connection_string}}) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
    return _clear


@pytest.fixture
def delete_s3_key():
    """Deletes S3 objects after E2E tests."""
    def _delete(config, key):
        bucket = config["s3"]["archive_bucket"]
        s3_client = get_s3_client(config)
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except Exception:
            logger.warning(f"⚠️ Could not delete S3 key {key} from bucket {bucket}")
    return _delete
