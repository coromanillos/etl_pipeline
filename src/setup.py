##############################################
# Title: Database setup script
# Author: Christopher Romanillos
# Description: Creates PostgreSQL tables
# for ETL pipeline using SQLAlchemy.
# Date: 11/23/24
# Version: 1.3
##############################################

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from utils.schema import Base
from utils.logging import get_logger  # <- Correct structured logger

# Load environment variables from a .env file
load_dotenv()

# Setup structured logger
logger = get_logger(module_name="setup.py")

# Retrieve PostgreSQL connection URL
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

if not POSTGRES_DATABASE_URL:
    logger.error("Environment variable not set", variable="POSTGRES_DATABASE_URL")
    sys.exit(1)

# Create SQLAlchemy engine
try:
    engine = create_engine(POSTGRES_DATABASE_URL)
    logger.info("Database engine created successfully")
except SQLAlchemyError as e:
    logger.exception("Failed to create database engine")
    sys.exit(1)

def create_tables(drop_existing=False):
    """Create (and optionally drop) PostgreSQL tables using SQLAlchemy metadata."""
    try:
        if drop_existing:
            logger.info("Dropping existing tables")
            Base.metadata.drop_all(engine)
            logger.info("Tables dropped successfully")

        logger.info("Creating tables")
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully")
    except SQLAlchemyError:
        logger.exception("Database setup failed during create_tables()")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting database setup process")
    create_tables(drop_existing=False)

