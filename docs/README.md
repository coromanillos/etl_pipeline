Project Premise: A local Savings Bank is looking to move their data to the cloud and leverage BI tools to create more detailed analytics. They want an IT professional to navigate the different technologies available in order to find an option that is:

Reliable; Data is ready to be used when needed (Sunday night /Monday early morning 12:00AM - 4:00 AM EST)

Accurate; Data

Medallion Architecture data design pattern is being used for this project. The goal is to organize and optimize the flow of data through different stages of the ETL pipeline to maximize the cost effectiveness to required performance ratio.

In the case of the previously mentioned project; given that the expected update schedule for data is weekly; where time is not a big constraint

First phase REST API to postgresql
Alpha Vantage Rest API is our data source, while postgresql is used as our staging ground. Python is used for the first ETL process between the two.
The main focus of this first phase is to clean data before it is further processed in the second phase.

Second phase postgresql to Redshift
postgresql is our local database run by docker, while Redshift is our cloud base data warehouse that will support end user interaction, via BI tools susch as Tableau, Google Sheets, Excel etc.
The main focus of this second phase is to ensure data is formatted and easily accessible for end users in the analytics department.

Considerations for Second phase (posrtgres to redshift)
Extraction: Extract as a CSV/Parquet, in this case CSV. when loading to Redshift
Validate Schema types, use IAM authentication-no password-based login.
Utilize the same standardized logging methods used in First phase ETL scripts.

## GOAL: Phase 2: Export from Postgres to CSV → upload to S3 → COPY into Redshift

Can you design for me an extract_postgres.py script that will extract data from postgres as a CSV?

When creating a load_redshift.py script would I use boto3? Is that the modern solution?

When would I use pydantic and why? Would I use it during the second ETL phase? If so, within what script would it be used in? the extraction, transformation or loading?

All scripts should use dotenv for config and .env managing.

IAM Role with S3 + Redshift permissions
Enable COPY from S3 in Redshift via REDSHIFT_ROLE_ARN and S3 bucket path.

# Planned scripts

## Phase 1: Dump data from Postgres to CSV

etl_postgres_to_csv.py

## Phase 2: Upload CSV to S3

etl_csv_to_s3.py

## Phase 3: COPY into Redshift from S3

etl_s3_to_redshift.py

## Planned Utility scripts:

db/ directory scripts

## psycopg2/sqlalchemy wrapper

postgres_conn.py

## redshift_connector wrapper

redshift_conn.py

aws/ directory

## wrapper for AWS SDK actions like uploading a file to S3

s3_utils.py

# utilities directory/

IAM authentication module
s3_utils.py

etl_project/
│
├── etl_api_to_postgres/
│ ├── extract_api.py
│ ├── transform_api_data.py
│ └── load_to_postgres.py
│
├── etl_postgres_to_redshift/
│ ├── extract_postgres.py
│ ├── transform_analytics_data.py
│ └── load_to_redshift.py
│
├── config/
│ └── config.yaml
│
├── db/
│ ├── postgres_connector.py # Logic to connect to your local or Docker-based Postgres
│ ├── redshift_connector.py # IAM-auth Redshift connection (calls from auth/ maybe)
│ └── s3_client.py # Boto3 client for file upload/download
│
├── aws/
│ ├── s3_utils.py
│ ├── iam_auth.py
│ └── boto_session.py
│
├── auth/
│ └── iam_auth.py # IAM auth/token logic
│
├── utils/
│ ├── logging.py
│ └── maybe custom decorators or helpers
│
└── main.py

# What to double check before testing:

- docker-compose.yml is correct and at root of project
- .env file has correct values
- Dockerfile that builds my app
  - It should include Python, dependencies, and copy the code.

# Once verified:

- Two options for test run with Docker: one-time and background process

# Testing 4/25

- Open Docker Desktop, once 'engine is running' in bottome left; in bash 'docker ps'
- Return to Docker Desktop, restart.
- Make sure you have WSL 2 installed on windows/Linux, and that under the Settings/Resources/WSL Integration/ directory, Integration with my default WSL distro is enabled.
