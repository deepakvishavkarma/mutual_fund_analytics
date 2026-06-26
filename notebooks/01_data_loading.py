import pandas as pd
import os

# List your 10 CSV files
csv_files = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

dataframes = {}
anomalies = []

for file in csv_files:
    path = f"C:/Users/Dell/mutual_fund_analytics/data/raw/{file}"
    if os.path.exists(path):
        df = pd.read_csv(path)
        name = file.replace(".csv", "")
        dataframes[name] = df
        
        print(f"\n{'='*50}")
        print(f"📁 FILE: {file}")
        print(f"Shape   : {df.shape}")
        print(f"\nDtypes:\n{df.dtypes}")
        print(f"\nHead:\n{df.head()}")
        
        # Check anomalies
        nulls = df.isnull().sum()
        if nulls.any():
            anomalies.append(f"{file}: {nulls[nulls > 0].to_dict()} nulls found")
        dups = df.duplicated().sum()
        if dups > 0:
            anomalies.append(f"{file}: {dups} duplicate rows found")
    else:
        print(f"File not found: {path}")

print("\n\n ANOMALY SUMMARY:")
for a in anomalies:
    print(f" {a}")
