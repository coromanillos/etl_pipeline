##############################################
# Title: SQLAlchemy Session Maker
# Author: Christopher Romanillos
# Description: Creates DB session using SQLAlchemy
# Date: 2025-07-06 | Version: 1.1
##############################################

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def build_postgres_conn_string(cfg: dict) -> str:
    pg = cfg["postgres_loader"]
    return f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"

def get_db_session(config: dict, engine_factory=create_engine, session_factory=sessionmaker):
    if not config:
        raise ValueError("❌ No config provided to get_db_session()")

    try:
        database_url = build_postgres_conn_string(config)
    except KeyError as e:
        logger.error(f"❌ Missing key in config to build connection string: {e}", exc_info=True)
        raise

    try:
        logger.debug(f"Creating SQLAlchemy engine for: {database_url}")
        engine = engine_factory(database_url)
        SessionLocal = session_factory(bind=engine)
        logger.info("✅ SQLAlchemy session factory created successfully.")
        return SessionLocal
    except SQLAlchemyError as e:
        logger.error(f"❌ SQLAlchemy engine creation failed: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in get_db_session(): {e}", exc_info=True)
        raise
