##############################################
# Title: Redshift Loader Script
# Author: Christopher Romanillos
# Description: Loads cleaned data into Redshift
# Date: 04/18/25
# Version: 1.0
##############################################

import os
import sys
import yaml
import redshift_connector
from dotenv import load_dotenv
import pandas as pd
from test_src.utils.logging import get_logger  # Adjusted import path for logging

# Load environment variables from the .env file
load_dotenv()

# Setup structured logger from your logging script
logger = get_logger(module_name="redshift_loader.py", log_file_path="logs/redshift_loader.log") 

# Retrieve Redshift connection details from environment variables
REDSHIFT_HOST = os.getenv("REDSHIFT_HOST")
REDSHIFT_PORT = os.getenv("REDSHIFT_PORT")
REDSHIFT_DB = os.getenv("REDSHIFT_DB")
REDSHIFT_USER = os.getenv("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD")
REDSHIFT_SCHEMA = os.getenv("REDSHIFT_SCHEMA")

if not all([REDSHIFT_HOST, REDSHIFT_PORT, REDSHIFT_DB, REDSHIFT_USER, REDSHIFT_PASSWORD]):
    logger.error("Missing Redshift connection details.")
    sys.exit(1)

# Establish a connection to Redshift
try:
    conn = redshift_connector.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )
    logger.info("Successfully connected to Redshift.")
except Exception as e:
    logger.exception("Failed to connect to Redshift.")
    sys.exit(1)

# Example query: load data into a pandas DataFrame (if needed)
try:
    query = "SELECT * FROM your_table LIMIT 10;"
    df = pd.read_sql(query, conn)
    logger.info(f"Data loaded into DataFrame: {df.shape[0]} rows.")
except Exception as e:
    logger.exception("Error while fetching data from Redshift.")
    sys.exit(1)

# Example: Insert transformed data into Redshift
try:
    # Assuming your transformed data is in `df`
    insert_query = """
    COPY your_table FROM 's3://your-bucket/your-file.csv'
    IAM_ROLE 'arn:aws:iam::your-aws-account-id:role/your-role'
    CSV
    DELIMITER ','
    IGNOREHEADER 1;
    """
    cursor = conn.cursor()
    cursor.execute(insert_query)
    logger.info("Data inserted successfully into Redshift.")
except Exception as e:
    logger.exception("Error while inserting data into Redshift.")
    sys.exit(1)
