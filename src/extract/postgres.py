import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
import os

load_dotenv()

def extract_table_from_postgres(table_name: str, schema: str = "public") -> pd.DataFrame:
    db_url = os.getenv("DATABASE_URL")
    engine = sqlalchemy.create_engine(db_url)
    query = f'SELECT * FROM "{schema}"."{table_name}"'
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df
