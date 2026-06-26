import pandas as pd
import os
import time

df = pd.read_csv("c:/Users/Dell/mutual_fund_analytics/data/raw/02_nav_history.csv")
print("Original shape:", df.shape)

# Parse dates
df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["date"])

# Sort
df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# Forward-fill missing NAV
df["nav"] = df.groupby("amfi_code")["nav"].ffill()

# Remove duplicates
df = df.drop_duplicates(subset=["amfi_code", "date"])

# Validate NAV > 0
invalid = df[df["nav"] <= 0]
print(f" Invalid NAV rows removed: {len(invalid)}")
df = df[df["nav"] > 0]

df.to_csv("c:/Users/Dell/mutual_fund_analytics/data/processed/nav_history_clean.csv", index=False)
print("Saved.Final shape:", df.shape)
