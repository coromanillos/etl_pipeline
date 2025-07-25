# ETL Pipeline for Alpha Vantage Stock Data 📈

A production-ready ETL pipeline that extracts, transforms, and loads stock market data from the [Alpha Vantage API](https://www.alphavantage.co/#about) into both a data warehouse and data lake.

The pipeline runs in two phases:
- From the REST API to a PostgreSQL staging area
- From PostgreSQL to AWS S3 and Amazon Redshift

It's fully containerized with Docker and orchestrated via Apache Airflow, with built-in logging and automated testing.

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

This project showcases a production-grade ETL pipeline designed with modern data engineering practices. It implements:

- Data cleaning and validation before loading to cloud services
- A medallion-style architecture with multiple ETL layers
- Ingestion from external API (JSONs)
- Efficient, cloud-optimized Parquet file handling
- A modular, testable, and fully containerized codebase for easy deployment

---

## Features

- Connects to Alpha Vantage and other REST APIs
- Handles API rate limiting and automatic retries
- Cleans, validates, and transforms raw financial data
- Loads data into AWS S3 (data lake) and Redshift (data warehouse)
- Supports automated weekly scheduling via Airflow or cron
- Full logging and audit tracking per ETL step
- Sends real-time alerts to Slack
- Includes unit, integration, and end-to-end test coverage

---

## Architecture

This ETL pipeline runs in **two main stages**, each with its own extraction, transformation, and loading steps.

---

### 🟦 **Stage 1: API to PostgreSQL (Staging Layer)**

#### 1. Extraction
- Extracts intraday stock data from the Alpha Vantage REST API
- Uses a centralized config file to define API parameters
- Supports dependency injection for easier testing (`fetch_fn`)
- Implements logging for success and failure states

#### 2. Transformation
- Validates required fields (`open`, `high`, `low`, `close`, `volume`)
- Normalizes field names and converts types (`str` → `float`, `datetime`, etc.)
- Filters out invalid rows with logging
- Uses multithreading to optimize parsing speed

#### 3. Loading
- Transformed records are converted into SQLAlchemy ORM objects
- Bulk inserts into a PostgreSQL staging table using `session.bulk_save_objects()`
- Logs total inserted vs. skipped rows

---

### 🟩 **Stage 2: PostgreSQL to Cloud Storage (S3 & Redshift)**

#### 1. Extraction
- Reads validated records from the PostgreSQL staging table
- Converts query results into pandas DataFrames

#### 2. Transformation
- Allows for further cleaning depending on user needs
- Converts data into columnar **Parquet format** for storage and cost efficient cloud storage
- Adds partitioning metadata (e.g., `symbol`, `date`) if applicable

#### 3. Loading
- Consists of two seperate DAGs that load data to S3 and Redshift respectively,
    - This eliminates the cost that would be incurred if data was loaded from S3 to Redshift*
    - Modular approach, add or remove a DAG as needed.
- Loads Parquet files, being sure to open only when needed, then close as soons as the operation completes. Optimal cost per opened
- Each step includes error handling and logging for observability

---

### 🛠️ Scheduling & Orchestration
- All ETL tasks are orchestrated using **Apache Airflow**
- DAGs are modular and reusable for weekly or ad-hoc scheduling
- Logging is handled via Python’s `logging` module and Airflow task logs

---

## Data Sources 

###  API: Time Series Intraday (JSON)
- **Endpoint:** `https://api.bank.com/transactions`
- **Fields:** `open`, `high`, `low`, `close`, `volume`

---

## Tech Stack 

- **Language:** Python >3.10
- **Libraries:** `pandas`, `requests`, `sqlalchemy`, `psycopg2`
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Apache Airflow
- **Storage:** PostgreSQL, AWS S3, Redshift
- **Alerting:** Slack 
- **Testing:** `pytest`, `Makefile`, Docker Compose

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
```

## Future Features
- Working with data that requires a NoSQL database (MongoDB)
- Different cloud provider GCS?