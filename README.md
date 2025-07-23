# ETL Pipeline for Alpha Vantage Stock Data 📈

A production-ready ETL pipeline that extracts, transforms, and loads stock market data from the [Alpha Vantage API](https://www.alphavantage.co/#about) into a PostgreSQL database. The pipeline is fully containerized with Docker, and orchestrated using Apache Airflow. This project also includes automated logging and testing.

---

## Table of Contents 

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Data Sources](#data-sources)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Running Tests](#running-tests)
- [Future Features](#future-features)

---

## Overview 

This project demonstrates a real-world ETL pipeline, built with best practices in mind for data engineering workflows. It includes:

- Automated pipeline
- Data ingestion from JSON REST API
- Medallion Architecture (Multiple ETL steps)
- Cloud-ready efficient loading strategies 
- Modular, testable, and containerized codebase

---

## Features 

-  Connects to multiple APIs and internal data files
-  Handles API rate limits and retries
-  Cleans and normalizes raw financial data
-  Loads to both a cloud data warehouse and data lake (AWS S3 & Redshift)
-  Automated weekly runs with Airflow or `cron`
-  Full logging and auditing for each step
-  Realtime messaging via Slack
-  Includes unit, integration, and end-to-end tests

---

## Architecture 

### 1. Extraction
- Extracts intraday time series data from the Alpha Vantage REST API
- Uses a centralized config file to define API parameters
- Supports dependency injection for easier testing (`fetch_fn`)
- Implements logging for successful or failed API calls

### 2. Transformation
- Validates that all required fields (`open`, `high`, `low`, `close`, `volume`) are present
- Normalizes keys and converts data types (e.g., strings to `float`, `int`, and `datetime`)
- Converts timestamp strings into Python `datetime` objects
- Uses multithreaded processing for efficient transformation
- Excludes and logs rows that fail validation or parsing

### 3. Loading
- Converts transformed data into SQLAlchemy ORM model instances (`IntradayData`)
- Uses `session.bulk_save_objects()` to efficiently load records into PostgreSQL
- Parses all numeric and datetime values before insertion
- Logs the number of inserted and skipped records, with detailed error handling

### 4. Scheduling & Orchestration
- Orchestrated and scheduled with **Apache Airflow** 
- Logging handled by Python’s built-in `logging`

---

## Data Sources 

###  API: Transaction Records (CSV)
- **Endpoint:** `https://api.bank.com/transactions`
- **Fields:** `transaction_id`, `account_number`, `amount`, `timestamp`, `category`
- **Auth:** API Key

###  API: Customer Info (JSON)
- **Endpoint:** `https://api.bank.com/customers`
- **Fields:** `customer_id`, `name`, `dob`, `address`, `phone_number`, `email`
- **Auth:** OAuth 2.0

###  Internal CSV: Savings Account Data
- **Path:** `/data/savings_accounts.csv`

###  Internal JSON: Customer Metadata
- **Path:** `/data/customers_metadata.json`

---

## Tech Stack 

- **Language:** Python 3.11
- **Libraries:** `pandas`, `requests`, `sqlalchemy`, `psycopg2`, `loguru`
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Apache Airflow, cron
- **Storage:** PostgreSQL, AWS S3, Redshift, Snowflake
- **Monitoring:** ELK Stack, Prometheus (optional)
- **Testing:** `pytest`, `Makefile`

---

## Getting Started 

```bash
# Clone the repo
git clone https://github.com/your-username/etl_pipeline.git
cd etl_pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in API keys, database URIs, etc.

# Run manually (optional)
python run_pipeline.py

```

## Future Features