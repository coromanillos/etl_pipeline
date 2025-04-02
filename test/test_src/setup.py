##############################################
# Title: Database setup script
# Author: Christopher Romanillos
# Description: Creates PostgreSQL tables
# for ETL pipeline using SQLAlchemy.
# Date: 11/23/24
# Version: 1.2
##############################################

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from utils.schema import Base 
from dotenv import load_dotenv
from utils import logger  # Use structlog logger

# Load environment variables from a .env file
load_dotenv()

# Set PostgreSQL database URL from environment
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
if not POSTGRES_DATABASE_URL:
    logger.error("POSTGRES_DATABASE_URL is not set in the environment.")
    sys.exit(1)  # Exit with error for Docker

# Create the engine to connect to PostgreSQL
try:
    engine = create_engine(POSTGRES_DATABASE_URL)
    logger.info("Database engine created successfully.")
except SQLAlchemyError as e:
    logger.error("Error creating database engine", exc_info=True)
    sys.exit(1)

def create_tables(drop_existing=False):
    """Create database tables in PostgreSQL"""
    try:
        if drop_existing:
            logger.info("Dropping existing tables...")
            Base.metadata.drop_all(engine)
            logger.info("Tables dropped successfully.")
        
        logger.info("Creating tables...")
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully.")
    except SQLAlchemyError as e:
        logger.error("Database setup failed", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting database setup...")
    try:
        create_tables(drop_existing=False)
        logger.info("Database setup completed successfully.")
    except Exception as e:
        logger.error("An error occurred during setup", exc_info=True)
        sys.exit(1)  # Ensure proper exit for Docker error handling
