import pandas as pd
import gzip
import json
from pathlib import Path

def convert_df_to_json(df: pd.DataFrame, output_path: Path):
    with gzip.open(output_path, "wt", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f)
