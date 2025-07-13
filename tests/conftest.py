# conftest.py

import pytest
import yaml
import logging
from src.utils.s3_client import get_s3_client

@pytest.fixture(scope="session")
def test_config():
    """Loads the test configuration from YAML once per session."""
    with open("config/test/test_rest_config.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture
def clear_table():
    """
    Reusable fixture to clear a PostgreSQL table before a test.
    Usage: clear_table(config, 'table_name')
    """
    def _clear(config, table_name):
        from src.utils.db_client import get_postgres_connection
        conn = get_postgres_connection(config)
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {table_name};")
            conn.commit()
    return _clear

@pytest.fixture
def drop_all_tables():
    """
    Reusable fixture to drop all tables in the PostgreSQL schema before a test.
    Usage: drop_all_tables(config, logger)
    """
    def _drop(config, logger):
        from src.utils.postgres_extractor import get_postgres_connection
        schema = config["postgres_loader"].get("schema", "public")
        database_url = config["postgres_loader"]["connection_string"]

        query = f"""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = '{schema}') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS {schema}.' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """

        try:
            with get_postgres_connection(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    conn.commit()
                    logger.info(f"✅ Dropped all tables in schema '{schema}'.")
        except Exception as e:
            logger.error(f"❌ Failed to drop tables: {e}", exc_info=True)
            raise

    return _drop

@pytest.fixture
def vacuum_postgres():
    """
    Reusable fixture to run VACUUM FULL on PostgreSQL before/after a test.
    Usage: vacuum_postgres(config, logger)
    """
    def _vacuum(config, logger):
        from src.utils.postgres_extractor import get_postgres_connection
        database_url = config["postgres_loader"]["connection_string"]

        try:
            with get_postgres_connection(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("VACUUM FULL;")
                    conn.commit()
                    logger.info("✅ VACUUM FULL executed successfully.")
        except Exception as e:
            logger.error(f"❌ VACUUM failed: {e}", exc_info=True)
            raise

    return _vacuum

@pytest.fixture
def clear_redshift_table():
    """
    Reusable fixture to drop a Redshift table before a test.
    Usage: clear_redshift_table(config, 'table_name')
    """
    def _clear(config, table_name):
        from src.utils.redshift_client import get_redshift_connection
        schema = config["redshift"]["schema"]
        query = f"DROP TABLE IF EXISTS {schema}.{table_name};"
        with get_redshift_connection(config) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
    return _clear

@pytest.fixture
def delete_s3_key():
    """
    Reusable fixture to delete a file from S3 after a test.
    Usage: delete_s3_key(config, s3_key)
    """
    def _delete(config, key):
        bucket = config["s3"]["archive_bucket"]
        s3_client = get_s3_client(config)
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except Exception:
            logging.warning(f"⚠️ Could not delete S3 key {key} from bucket {bucket}")
    return _delete
