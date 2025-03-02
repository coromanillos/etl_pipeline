# README - Savings Bank Data Pipeline

## Project Overview

A savings bank employer has tasked you with designing a data pipeline that extracts data from multiple sources, performs ETL/ELT tasks to clean and process the data, and uploads new records weekly to a cloud data warehouse. The extracted data comes from the following sources:

- **Two REST APIs** (one returning CSV data, the other returning JSON data)
- **A CSV file** (internal transactional data)
- **A JSON file** (customer metadata)

The goal is to build an automated, maintainable, and scalable pipeline that ensures data integrity and consistency.

## Requirements

### Functional Requirements

- Extract data from:
  - API 1 (CSV format)
  - API 2 (JSON format)
  - Internal CSV file
  - Internal JSON file
- Transform and clean the data:
  - Handle missing or incorrect values
  - Normalize and structure data consistently
  - Ensure referential integrity between datasets
- Load transformed data into a cloud data warehouse (e.g., AWS Redshift, Snowflake, Google BigQuery)
- Schedule pipeline execution to run weekly
- Maintain logging and monitoring for debugging and performance tracking

### Non-Functional Requirements

- Pipeline should be modular and extensible
- Ensure data security and compliance with banking regulations
- Optimize performance for large datasets
- Handle API rate limits and failures gracefully

## Data Sources

### API 1 - Transaction Records (CSV Format)

- Endpoint: `https://api.bank.com/transactions`
- Fields: `transaction_id`, `account_number`, `amount`, `timestamp`, `category`
- Authentication: API key required

### API 2 - Customer Information (JSON Format)

- Endpoint: `https://api.bank.com/customers`
- Fields: `customer_id`, `name`, `dob`, `address`, `phone_number`, `email`
- Authentication: OAuth 2.0

### Internal CSV File - Savings Account Data

- Path: `/data/savings_accounts.csv`
- Fields: `account_number`, `customer_id`, `balance`, `account_type`, `last_updated`

### Internal JSON File - Customer Metadata

- Path: `/data/customers_metadata.json`
- Fields: `customer_id`, `risk_score`, `credit_rating`, `loan_eligibility`

## Pipeline Architecture

### 1. Extraction

- Use Python’s `requests` library to extract data from APIs.
- Read CSV and JSON files using `pandas`.
- Implement retries and exponential backoff for API calls.

### 2. Transformation

- Convert all timestamps to UTC format.
- Remove duplicate records and handle null values.
- Standardize categorical fields (e.g., account types, transaction categories).
- Ensure customer IDs and account numbers match across datasets.

### 3. Loading

- Use `psycopg2` or `sqlalchemy` to insert records into the cloud data warehouse.
- Maintain an audit log of inserted records.

### 4. Scheduling & Automation

- Use Apache Airflow or `cron` to schedule weekly execution.
- Implement logging with `loguru` or Python’s built-in `logging` module.

## Tech Stack

- **Containerization:** Docker (for creating, deploying, and running applications in containers, ensuring consistency across environments)
- **Programming Language:** Python
- **Libraries:** `requests`, `pandas`, `sqlalchemy`, `psycopg2`, `pyarrow`
- **Orchestration:** Apache Airflow / Cron Jobs
- **Storage & Processing:** AWS S3, Google Cloud Storage, Snowflake, AWS Redshift
- **Logging & Monitoring:** `loguru`, Prometheus, ELK Stack

## Deployment & Execution

1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/savings-bank-pipeline.git
   ```
2. Set up a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables (API keys, database credentials) in a `.env` file.
5. Run the pipeline manually for testing:
   ```sh
   python run_pipeline.py
   ```
6. Deploy to an orchestration tool (Airflow, cron job).

## Future Enhancements

- Implement data validation checks before loading into the warehouse.
- Add streaming capabilities for real-time processing.
- Integrate anomaly detection for fraudulent transactions.
- Implement data validation checks.
- Add support for additional data sources.
- Optimize database indexing for performance.

## Contributors

- **[Your Name]** - Data Engineer
- **Savings Bank IT Team**

---

This project is a prototype for internal use by the Savings Bank. Contact the IT department for questions and support.
