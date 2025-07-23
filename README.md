# ETL Pipeline for Alpha Vantage Stock Data 📈

A production-ready ETL pipeline that extracts, transforms, and loads stock market data from the Alpha Vantage API into a PostgreSQL database. The pipeline is fully containerized with Docker, orchestrated using Apache Airflow, and includes automated logging and testing.

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
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)

---

## Overview 

This project demonstrates a real-world ETL pipeline, built with best practices in mind for data engineering workflows. It includes:

- Data ingestion from multiple formats (JSON, CSV)
- Automated transformations and validation
- Cloud-ready loading strategies
- Modular, testable, and containerized codebase

---

## Features 

-  Connects to multiple APIs and internal data files
-  Handles API rate limits and retries
-  Cleans and normalizes raw financial data
-  Loads to a cloud data warehouse (PostgreSQL, Redshift, or Snowflake)
-  Automated weekly runs with Airflow or `cron`
-  Full logging and auditing for each step
-  Includes unit, integration, and end-to-end tests

---

## Architecture 

### 1. Extraction
- Uses `requests` to extract API data with retry/backoff
- Reads internal CSV/JSON using `pandas`

### 2. Transformation
- Cleans and normalizes fields
- Converts timestamps to UTC
- Handles nulls, duplicates, and categoricals

### 3. Loading
- Uses `sqlalchemy` or `psycopg2` to load data into PostgreSQL or cloud warehouses
- Maintains audit logs for inserts

### 4. Scheduling & Orchestration
- Orchestrated with **Apache Airflow** or scheduled with `cron`
- Logging handled by `loguru` or Python’s built-in `logging`

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
git clone https://github.com/your-username/savings-bank-pipeline.git
cd savings-bank-pipeline

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
