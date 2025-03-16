##############################################
# Title: Database Connection Setup
# Author: Christopher Romanillos
# Description: Handles the creation of the 
# database engine and sessions. 
# Date: 3/11/24
# Version: 1.0
##############################################

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging
import sys

# Configure logging to send logs to stdout
logging.basicConfig(
    level=logging.INFO,  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  # Ensures logs go to stdout for Docker to capture
)

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

if not DATABASE_URL:
    logging.error("DATABASE_URL is not set in the environment variables.")
    exit(1)

def get_db_session():
    """Returns a database session that can be used to interact with the database."""
    try:
        # Create the database engine
        engine = create_engine(DATABASE_URL)
        # Create session factory
        Session = sessionmaker(bind=engine)
        logging.info("Database connection established successfully.")
        return Session
    except Exception as e:
        logging.error(f"Failed to create database engine: {e}")
        exit(1)
