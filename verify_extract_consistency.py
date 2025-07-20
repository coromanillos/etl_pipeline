from src.utils.config import load_config
from src.etl_rest_to_postgres.extract import extract_data
from src.utils.api_requests import fetch_data


CONFIG_PATH = "./config/test/test_rest_config.yaml"

# Run through production extract_data
config = load_config(CONFIG_PATH)
data_from_extract = extract_data(config)

# Run through manual fetch directly
manual_data = fetch_data(config["api"])

# Simple comparison
if data_from_extract == manual_data:
    print("✅ Extracted data is consistent with manual API fetch.")
else:
    print("❌ Extracted data differs from manual API fetch.")

# Optional: show small diff if needed
import json
print("\nExtract Data Sample:\n", json.dumps(data_from_extract, indent=2)[:500])
print("\nManual Data Sample:\n", json.dumps(manual_data, indent=2)[:500])
