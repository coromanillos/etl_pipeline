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

def get_db_session(config: dict, engine_factory=create_engine, session_factory=sessionmaker):
    """
    Returns a SQLAlchemy session factory using injected engine and session factories.

    Args:
        config (dict): Config containing 'postgres_loader.connection_string'.
        engine_factory (callable): Dependency-injected engine creation (default: create_engine).
        session_factory (callable): Dependency-injected sessionmaker (default: sessionmaker).
    Returns:
        A session factory (callable) for creating SQLAlchemy sessions.
    """
    if not config:
        raise ValueError("❌ No config provided to get_db_session()")

    try:
        database_url = config["postgres_loader"]["connection_string"]
    except KeyError:
        logger.error("❌ 'connection_string' not found in config['postgres_loader']", exc_info=True)
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
