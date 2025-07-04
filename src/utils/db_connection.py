##############################################
# Title: Database Connection Setup
# Author: Christopher Romanillos
# Description: Handles the creation of the 
# database engine and sessions.
# Date: 3/11/24
# Version: 1.5
##############################################

import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Load environment variables for local development (ignored if running inside Docker with env)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("Missing environment variable: DATABASE_URL")
    raise EnvironmentError("DATABASE_URL is not set in environment variables.")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

logger.info("Database connection pool established")

def get_db_session():
    """Returns a database session for interacting with the database."""
    try:
        logger.info("Providing a session from the connection pool")
        return Session
    except Exception as e:
        logger.error("Failed to create database session", exc_info=True)
        raise
