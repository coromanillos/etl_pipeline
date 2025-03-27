##############################################
# Title: Database setup script
# Author: Christopher Romanillos
# Description: Creates PostgreSQL tables
# for ETL pipeline using SQLAlchemy.
# Date: 11/23/24
# Version: 1.1
##############################################

import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from utils.schema import Base 
from dotenv import load_dotenv
from pathlib import Path  # Import pathlib for modern file path handling

# Load environment variables from a .env file
load_dotenv()

# Configure logging for Docker compatibility (stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  # Ensures logs are captured by Docker
)

# Set PostgreSQL database URL from environment
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
if not POSTGRES_DATABASE_URL:
    logging.error("POSTGRES_DATABASE_URL is not set in the environment.")
    sys.exit(1)  # Exit with error for Docker

# Use pathlib to construct log file path, for example
log_path = Path(__file__).resolve().parent / '../logs/setup.log'
logging.info(f"Log file path: {log_path}")

# Create the engine to connect to PostgreSQL
try:
    engine = create_engine(POSTGRES_DATABASE_URL)
    logging.info("Database engine created successfully.")
except SQLAlchemyError as e:
    logging.error(f"Error creating database engine: {e}", exc_info=True)
    sys.exit(1)

def create_tables(drop_existing=False):
    """Create database tables in PostgreSQL"""
    try:
        if drop_existing:
            logging.info("Dropping existing tables...")
            Base.metadata.drop_all(engine)
            logging.info("Tables dropped successfully.")
        
        logging.info("Creating tables...")
        Base.metadata.create_all(engine)
        logging.info("Tables created successfully.")
    except SQLAlchemyError as e:
        logging.error(f"Database setup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    logging.info("Starting database setup...")
    try:
        create_tables(drop_existing=False)
        logging.info("Database setup completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during setup: {e}", exc_info=True)
        sys.exit(1)  # Ensure proper exit for Docker error handling
