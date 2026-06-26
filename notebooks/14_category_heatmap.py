import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/processed/transactions_clean.csv")
df["transaction_date"] = pd.to_datetime(df["transaction_date"])
df["month_label"] = df["transaction_date"].dt.strftime("%b %Y")
df["month_order"] = df["transaction_date"].dt.to_period("M")

# Merge with fund master to get category
master = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/raw/01_fund_master.csv")[["amfi_code", "category"]]
df = df.merge(master, on="amfi_code", how="left")

pivot = df.groupby(["category", "month_label"])["amount_inr"].sum().reset_index()
pivot_table = pivot.pivot(index="category", columns="month_label", values="amount_inr").fillna(0)

# Sort columns chronologically
pivot_table = pivot_table[sorted(pivot_table.columns,
    key=lambda x: pd.to_datetime(x, format="%b %Y"))]

plt.figure(figsize=(20, 8))
sns.heatmap(
    pivot_table / 1e7,
    cmap="YlOrRd", linewidths=0.3,
    cbar_kws={"label": "Net Inflow (₹ Cr)"},
    fmt=".0f", annot=False
)
plt.title("Category-wise Monthly Net Inflow Heatmap (2022–2025)")
plt.xlabel("Month")
plt.ylabel("Fund Category")
plt.xticks(rotation=45, ha="right", fontsize=7)
plt.tight_layout()
plt.savefig("c:/users/dell/mutual_fund_analytics/reports/charts/T4_category_heatmap.png", dpi=150)
print("✅ T4 saved")
