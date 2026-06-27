import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("C:/users/dell/mutual_fund_analytics/data/raw/09_portfolio_holdings.csv")

# Filter equity funds only
if "scheme_type" in df.columns:
    df = df[df["scheme_type"].str.lower().str.contains("equity", na=False)]

sector_weights = df.groupby("sector")["weight_pct"].sum().sort_values(ascending=False)

# Keep top 10 sectors, club rest as "Others"
top10 = sector_weights.head(10)
others = sector_weights.iloc[10:].sum()
if others > 0:
    top10["Others"] = others

colors = plt.cm.Set3.colors[:len(top10)]

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    top10, labels=top10.index, autopct="%1.1f%%",
    colors=colors, startangle=140,
    wedgeprops=dict(width=0.5),   # donut effect
    pctdistance=0.75
)

for text in autotexts:
    text.set_fontsize(9)

ax.set_title("Sector Allocation — Aggregate Across All Equity Funds", fontsize=13)
plt.tight_layout()
plt.savefig("C:/users/dell/mutual_fund_analytics/reports/charts/T9_sector_donut.png", dpi=150)
print("✅ T9 saved")
