##############################################
# Title: Database Connection Setup
# Author: Christopher Romanillos
# Description: Handles the creation of the 
# database engine and sessions.
# Date: 3/11/24
# Version: 1.5
##############################################

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.logging import get_logger

# Setup logging immediately with default configuration
logger = get_logger(__file__)

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

if not DATABASE_URL:
    logger.error("Missing environment variable", variable="POSTGRES_DATABASE_URL")
    raise EnvironmentError("POSTGRES_DATABASE_URL is not set in environment variables.")

# Create engine only once and reuse it for all sessions
engine = create_engine(DATABASE_URL)

# Session maker bound to the engine (session factory)
Session = sessionmaker(bind=engine)

logger.info("Database connection pool established")

def get_db_session():
    """Returns a database session for interacting with the database."""
    try:
        # Return the session factory, no need to recreate the engine
        logger.info("Providing a session from the connection pool")
        return Session
    except Exception as e:
        logger.error("Failed to create database session", error=str(e))
        raise
