##############################################
# Title: Database Connection Setup
# Author: Christopher Romanillos
# Description: Handles the creation of the 
# database engine and sessions. 
# Date: 3/11/24
# Version: 1.4
##############################################

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.logging import setup_logging, get_logger

# Setup logging immediately with default configuration
setup_logging()
logger = get_logger(__file__)

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
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
        raise
