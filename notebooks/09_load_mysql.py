import pandas as pd
from sqlalchemy import create_engine, text



engine = create_engine("mysql+pymysql://deepak:Devendra%4012@localhost/mf_analytics")

# Load CSVs
nav  = pd.read_csv("c:/Users/dell/mutual_fund_analytics/data/processed/nav_history_clean.csv")
txn  = pd.read_csv("c:/Users/dell/mutual_fund_analytics/data/processed/transactions_clean.csv")
perf = pd.read_csv("c:/Users/dell/mutual_fund_analytics/data/processed/performance_clean.csv")

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
