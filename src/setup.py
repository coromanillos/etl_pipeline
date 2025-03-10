##############################################
# Title: Database setup script
# Author: Christopher Romanillos
# Description: Creates 
# Date: 11/23/24
# Version: 1.0
##############################################

import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from schema import Base 
from dotenv import load_dotenv
import os 
from pathlib import Path

# Load environment variables from a .env file
load_dotenv()

# Configure logging
log_path = os.path.join(os.path.dirname(__file__), '../logs/setup.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set your PostgreSQL database URL
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
if not POSTGRES_DATABASE_URL:
    logging.error("DATABASE_URL is not set in the environment.")
    raise ValueError("DATABASE_URL is required but not set.")

# Create the engine to connect to PostgreSQL
try:
    engine = create_engine(POSTGRES_DATABASE_URL)
    logging.info("Database engine created successfully.")
except SQLAlchemyError as e:
    logging.error(f"Error creating database engine: {e}")
    raise

def create_tables(drop_existing=False):
    """Create database tables"""
    try:
        if drop_existing:
            Base.metadata.drop_all(engine)
            logging.info("Tables dropped successfully.")
        Base.metadata.create_all(engine)
        logging.info("Tables created successfully.")
    except SQLAlchemyError as e:
        logging.error(f"Error dropping tables: {e}")
        raise

if __name__ == "__main__":
    # Run the setup process
    logging.info("Starting database setup...")
    try:
        create_tables(drop_existing=False)
        logging.info("Database setup completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during setup: {e}")
