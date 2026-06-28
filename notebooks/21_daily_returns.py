import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("C:/users/dell/mutual_fund_analytics/data/processed/nav_history_clean.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["amfi_code", "date"])

# Compute daily return
df["daily_return"] = df.groupby("amfi_code")["nav"].pct_change()

# Drop NaN
df = df.dropna(subset=["daily_return"])

# Validate distribution
print("Daily Return Stats:")
print(df["daily_return"].describe())
print(f"\nAny >50% daily move (anomaly): {(df['daily_return'].abs() > 0.5).sum()}")

# Plot distribution
plt.figure(figsize=(10, 5))
sns.histplot(df["daily_return"], bins=100, kde=True, color="steelblue")
plt.axvline(0, color="red", linestyle="--", label="Zero")
plt.title("Distribution of Daily Returns — All 40 Schemes")
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig("C:/users/dell/mutual_fund_analytics/reports/charts/P0_daily_return_dist.png", dpi=150)

# Save for use by other scripts
df.to_csv("C:/users/dell/mutual_fund_analytics/data/processed/daily_returns.csv", index=False)
print("✅ Daily returns saved: C:/users/dell/mutual_fund_analytics/data/processed/daily_returns.csv")
