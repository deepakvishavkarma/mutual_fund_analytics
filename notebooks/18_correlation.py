import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("C:/users/dell/mutual_fund_analytics/data/processed/nav_history_clean.csv")
df["date"] = pd.to_datetime(df["date"])

# Pick 10 funds
top10_codes = df["amfi_code"].value_counts().head(10).index.tolist()
df10 = df[df["amfi_code"].isin(top10_codes)]

# Pivot: rows=date, cols=fund
pivot = df10.pivot(index="date", columns="amfi_code", values="nav")

# Daily returns
returns = pivot.pct_change().dropna()

# Rename columns to scheme names if available
if "scheme_name" in df.columns:
    name_map = df[["amfi_code", "scheme_name"]].drop_duplicates().set_index("amfi_code")["scheme_name"]
    returns.columns = [name_map.get(c, str(c))[:20] for c in returns.columns]

corr = returns.corr()

plt.figure(figsize=(12, 9))
sns.heatmap(
    corr, annot=True, fmt=".2f",
    cmap="coolwarm", center=0,
    linewidths=0.5, square=True,
    cbar_kws={"label": "Pearson Correlation"}
)
plt.title("Pairwise Correlation of Daily Returns — Top 10 Funds")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig("C:/users/dell/mutual_fund_analytics/reports/charts/T8_correlation.png", dpi=150)
print("✅ T8 saved")
