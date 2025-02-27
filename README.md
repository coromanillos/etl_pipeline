# ETL Project

## Project Overview

This ETL (Extract, Transform, Load) project extracts financial data from the Alpha Vantage REST API, processes it for consistency and integrity, and loads it into a PostgreSQL database for further analysis. The pipeline runs on a scheduled basis using cron jobs.

## Project Structure

```
/etl_project
│── config/            # Configuration files (.yaml, .env)
│── data/              # Raw and prepared data storage
│── docs/              # Documentation
│── logs/              # Logging output
│── notebooks/         # Jupyter notebooks for testing and analysis
│── src/               # Source code for ETL scripts
│── tests/             # Unit tests
│── .env               # Environment variables
│── README.md          # Project documentation
│── requirements.txt   # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.x
- PostgreSQL
- Alpha Vantage API Key
- Virtual Environment (Recommended)

### Installation

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd etl_project
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` (use `.env.example` as a reference).

## Usage

### Running the ETL Pipeline

```sh
python src/extract.py  # Extract data from API
python src/transform.py  # Clean and prepare data
python src/load.py  # Load data into PostgreSQL
```

Alternatively, set up a cron job for scheduled execution.

### Logging

Logs are stored in the `logs/` directory and capture extraction times, errors, and processing details.

## Configuration

- `config/config.yaml`: Stores API and database connection details.
- `.env`: Contains sensitive credentials.

## Testing

Run unit tests using:

```sh
pytest tests/
```

## Future Improvements

- Implement data validation checks.
- Add support for additional data sources.
- Optimize database indexing for performance.

## License

This project is licensed under the MIT License.

## Contact

For questions, reach out via [your contact information].
