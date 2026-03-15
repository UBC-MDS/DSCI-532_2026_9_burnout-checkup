import pandas as pd
from src.data import load_dashboard_data

df = load_dashboard_data()
df.to_parquet("data/processed/employees.parquet", index=False)
print(f"Saved {len(df)} rows to parquet")