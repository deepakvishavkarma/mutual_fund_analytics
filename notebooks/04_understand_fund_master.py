import pandas as pd

df_master = pd.read_csv("C:/Users/Dell/mutual_fund_analytics/data/raw/01_fund_master.csv")

print("=" * 50)
print("FUND HOUSES:", df_master["fund_house"].nunique())
print(df_master["fund_house"].value_counts().head(10))

print("\nCATEGORIES:", df_master["category"].nunique())
print(df_master["category"].value_counts())

print("\nSUB-CATEGORIES:")
if "scheme_sub_category" in df_master.columns:
    print(df_master["sub_category"].value_counts())

print("\nRISK GRADES:")
if "risk_grade" in df_master.columns:
    print(df_master["risk_category"].value_counts())

# AMFI Code Structure
print("\nSCHEME CODE RANGE:")
print(f"  Min: {df_master['sebi_category_code'].min()}")
print(f"  Max: {df_master['sebi_category_code'].max()}")
print(f"  Total Schemes: {df_master['sebi_category_code'].nunique()}")
