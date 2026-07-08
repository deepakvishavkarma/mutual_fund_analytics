from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text

ROOT      = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

# Read credentials from environment variables — never hard-code
user     = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "yourpassword")
host     = os.getenv("MYSQL_HOST", "localhost")
db       = os.getenv("MYSQL_DB", "mf_analytics")

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}")

# Load CSVs
nav  = pd.read_csv(PROCESSED / "nav_history_clean.csv")
txn  = pd.read_csv(PROCESSED / "transactions_clean.csv")
perf = pd.read_csv(PROCESSED / "performance_clean.csv")

# Push to MySQL
print("Loading nav...")
nav.to_sql("fact_nav", engine, if_exists="replace", index=False)

print("Loading transactions...")
txn.to_sql("fact_transactions", engine, if_exists="replace", index=False)

print("Loading performance...")
perf.to_sql("fact_performance", engine, if_exists="replace", index=False)

# Verify row counts
print("\n ROW COUNT VERIFICATION")
with engine.connect() as conn:
    for table, df in [("fact_nav", nav), ("fact_transactions", txn), ("fact_performance", perf)]:
        db_count  = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
        csv_count = len(df)
        status    = "CORRECT" if db_count == csv_count else "MISMATCH"
        print(f"{status}  {table}: CSV={csv_count} | DB={db_count}")
