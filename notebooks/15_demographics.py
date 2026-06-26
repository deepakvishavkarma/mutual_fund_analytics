import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/raw/08_investor_transactions.csv")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Investor Demographics Analysis", fontsize=14, fontweight="bold")

# Chart 1: Age group pie
age_counts = df["age_group"].value_counts()
axes[0].pie(age_counts, labels=age_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette("pastel"), startangle=140)
axes[0].set_title("Age Group Distribution")

# Chart 2: SIP amount box plot by age group
sip_df = df[df["transaction_type"] == "SIP"]
sns.boxplot(data=sip_df, x="age_group", y="amount_inr",
            palette="Set2", ax=axes[1])
axes[1].set_title("SIP Amount by Age Group")
axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("SIP Amount (₹)")
axes[1].tick_params(axis="x", rotation=30)

# Chart 3: Gender split
gender_counts = df["gender"].value_counts()
axes[2].pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%",
            colors=["#74b9ff", "#fd79a8"], startangle=90)
axes[2].set_title("Gender Split")

plt.tight_layout()
plt.savefig("c:/users/dell/mutual_fund_analytics/reports/charts/T5_demographics.png", dpi=150)
print("✅ T5 saved")
