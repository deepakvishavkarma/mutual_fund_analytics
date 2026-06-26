import pandas as pd
df_master = pd.read_csv("C:/Users/Dell/mutual_fund_analytics/data/raw/01_fund_master.csv")
df_nav = pd.read_csv("C:/Users/Dell/mutual_fund_analytics/data/raw/02_nav_history.csv")

master_codes = set(df_master["amfi_code"].unique())
nav_codes = set(df_nav["amfi_code"].unique())

codes_in_master_not_nav = master_codes - nav_codes
codes_in_nav_not_master = nav_codes - master_codes

# Print summary
print("=" * 50)
print("DATA QUALITY SUMMARY — Day 1")
print("=" * 50)
print(f"Total schemes in fund_master    : {len(master_codes)}")
print(f"Total schemes in nav_history    : {len(nav_codes)}")
print(f"Codes in master but NOT in nav  : {len(codes_in_master_not_nav)}")
print(f"Codes in nav but NOT in master  : {len(codes_in_nav_not_master)}")

if codes_in_master_not_nav:
    print(f"\n Missing from nav_history: {list(codes_in_master_not_nav)[:10]}")
else:
    print("\n All fund_master codes are present in nav_history")

# Save summary
summary = {
    "total_master_codes": len(master_codes),
    "total_nav_codes": len(nav_codes),
    "missing_from_nav": len(codes_in_master_not_nav),
    "extra_in_nav": len(codes_in_nav_not_master),
    "missing_codes": list(codes_in_master_not_nav)
}

import json
with open("C:/Users/Dell/mutual_fund_analytics/reports/day1_data_quality.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n Quality report saved to reports/day1_data_quality.json")
