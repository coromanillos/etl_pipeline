import pandas as pd
from sqlalchemy import create_engine
import os

def extract_postgres_to_file(config, logger, output_path: str):
    engine = create_engine(config["postgres_loader"]["connection_string"])
    query = f'SELECT * FROM {config["postgres_loader"]["schema"]}.{config["postgres_loader"]["table"]}'
    
    logger.info(f"Querying PostgreSQL: {query}")
    df = pd.read_sql(query, engine)
    
    df.to_json(output_path, orient='records', lines=True)
    logger.info(f"Data written to {output_path}")
    
    return output_path
