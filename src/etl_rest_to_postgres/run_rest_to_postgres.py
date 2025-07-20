# run_rest_to_postgres.py wrapper
import logging
import sys
from src.utils.config import load_config
from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.load import load_data

logger = logging.getLogger(__name__)


def run_pipeline(config_path: str):
    config = load_config(config_path)
    if not config:
        logger.error("Failed to load config, aborting pipeline.")
        sys.exit(1)

    raw_data = extract_data(config)
    if not raw_data:
        logger.error("Extraction failed, aborting pipeline.")
        sys.exit(1)

    required_fields = config.get("transform", {}).get("required_fields", [])
    processed_data, failed_items = process_raw_data(raw_data, config, required_fields)
    if not processed_data:
        logger.error("Transformation failed, aborting pipeline.")
        sys.exit(1)

    inserted = load_data(processed_data, config)
    if inserted == 0:
        logger.error("Loading failed or no records inserted.")
        sys.exit(1)

    logger.info(f"Pipeline completed successfully. Records inserted: {inserted}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run REST to Postgres ETL pipeline")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to pipeline config file (YAML/JSON)"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    run_pipeline(args.config)
