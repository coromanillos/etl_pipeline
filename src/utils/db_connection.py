##############################################
# Title: PostgreSQL Connection Module
# Author: Christopher Romanillos
# Description: Session maker for SQLAlchemy
# Date: 2025-07-04
# Version: 2.0 (No .env, Docker-safe)
##############################################

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.config import get_env_var

logger = logging.getLogger(__name__)

DATABASE_URL = get_env_var("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    logger.info("✅ PostgreSQL connection pool initialized")
except Exception as e:
    logger.error("❌ Failed to initialize database engine", exc_info=True)
    raise

def get_db_session():
    try:
        logger.debug("📦 Providing new DB session")
        return Session
    except Exception as e:
        logger.error("❌ Failed to create DB session", exc_info=True)
        raise