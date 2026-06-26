import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/processed/transactions_clean.csv")

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Geographic Distribution of SIP Investments", fontsize=14, fontweight="bold")

# Chart 1: SIP by state (horizontal bar)
state_sip = df[df["transaction_type"] == "SIP"] \
    .groupby("state")["amount_inr"].sum().sort_values(ascending=True)

state_sip.plot(kind="barh", ax=axes[0], color="steelblue")
axes[0].set_title("SIP Amount by State")
axes[0].set_xlabel("Total SIP Amount (₹)")
axes[0].set_ylabel("State")

# Chart 2: T30 vs B30 pie
if "city_tier" in df.columns:
    tier_counts = df.groupby("city_tier")["amount_inr"].sum()
    axes[1].pie(tier_counts, labels=tier_counts.index, autopct="%1.1f%%",
                colors=["#0984e3", "#00b894"], startangle=90)
    axes[1].set_title("T30 vs B30 City Tier Split")
else:
    axes[1].text(0.5, 0.5, "city_tier column\nnot found in data",
                 ha="center", va="center", fontsize=12)
    axes[1].set_title("T30 vs B30 (Data Missing)")

plt.tight_layout()
plt.savefig("c:/users/dell/mutual_fund_analytics/reports/charts/T6_geographic.png", dpi=150)
print("✅ T6 saved")
