import requests
import pandas as pd

# Fetch HDFC Top 100 Direct - AMFI code 125497
url = "https://api.mfapi.in/mf/125497"
response = requests.get(url)
data = response.json()

# Parse
meta = data["meta"]
nav_records = data["data"]  # list of {"date": "...", "nav": "..."}

df_nav = pd.DataFrame(nav_records)
df_nav["scheme_code"] = meta["scheme_code"]
df_nav["scheme_name"] = meta["scheme_name"]
df_nav["fund_house"] = meta["fund_house"]
df_nav["scheme_category"] = meta["scheme_category"]
df_nav["scheme_type"] = meta["scheme_type"]

# Save
df_nav.to_csv("C:/Users/Dell/mutual_fund_analytics/data/raw/hdfc_top100_nav.csv", index=False)

print(f" Saved: {len(df_nav)} NAV records")
print(f"Fund: {meta['scheme_name']}")
print(f"Category: {meta['scheme_category']}")
print(df_nav.head())
