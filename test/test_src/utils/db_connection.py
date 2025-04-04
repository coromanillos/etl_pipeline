##############################################
# Title: Database Connection Setup
# Author: Christopher Romanillos
# Description: Handles the creation of the 
# database engine and sessions. 
# Date: 3/11/24
# Version: 1.1
##############################################

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import structlog

# Configure structlog for clean, structured JSON-style logs
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Load environment variables from .env file
load_dotenv()

# Get the database URL
DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

if not DATABASE_URL:
    logger.error("Missing environment variable", variable="POSTGRES_DATABASE_URL")
    raise EnvironmentError("POSTGRES_DATABASE_URL is not set in environment variables.")

def get_db_session():
    """Returns a database session factory for interacting with the database."""
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        logger.info("Database connection established")
        return Session
    except Exception as e:
        logger.error("Failed to create database session", error=str(e))
        raise  # Reraise to let the caller handle it if needed
