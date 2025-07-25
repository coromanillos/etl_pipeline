# test_alpha_vantage_extract.py

import json
import requests
from src.utils.config import load_config
from src.etl_rest_to_postgres.extract import extract_data


def run_etl_extract_test(config_path: str):
    """
    Run the ETL extract function with the provided config file.
    """
    try:
        config = load_config(config_path)
        data = extract_data(config)
        print("\nETL Extract Success:\n")
        print(json.dumps(data, indent=2)[:2000])  # Print first 2000 chars for readability
    except Exception as e:
        print(f"\nETL Extract Error: {e}")


def fetch_data(api_config: dict) -> dict:
    """
    Manually fetch data from Alpha Vantage API (bypasses ETL function).
    """
    base_url = api_config.get("base_url", "https://www.alphavantage.co/query")
    params = {
        "function": api_config.get("function", "TIME_SERIES_INTRADAY"),
        "symbol": api_config.get("symbol", "IBM"),
        "interval": api_config.get("interval", "5min"),
        "apikey": api_config.get("apikey"),
        "datatype": "json"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def run_manual_api_test():
    """
    Manually test Alpha Vantage API connection.
    """
    api_config = {
        "apikey": "YOUR_ALPHA_VANTAGE_API_KEY",  # Replace with your actual key for manual test
        "function": "TIME_SERIES_INTRADAY",
        "symbol": "IBM",
        "interval": "5min",
    }

    try:
        data = fetch_data(api_config)
        print("\nManual API Call Success:\n")
        print(json.dumps(data, indent=2)[:2000])
    except Exception as e:
        print(f"\nManual API Call Error: {e}")


if __name__ == "__main__":
    # Toggle between ETL extract test and manual API test here:
    CONFIG_PATH = "./config/test/test_rest_config.yaml"
    
    run_etl_extract_test(CONFIG_PATH)
    # run_manual_api_test()  # Uncomment to run manual API test
