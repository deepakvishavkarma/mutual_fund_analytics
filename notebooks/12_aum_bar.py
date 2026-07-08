from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RAW=ROOT/"data"/"raw"
PROCESSED=ROOT/"data"/"processed"
CHARTS=ROOT/"reports"/"charts"
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

df = pd.read_csv(RAW / "03_aum_by_fund_house.csv")
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df = df[df["year"].between(2022, 2025)]

aum_grouped = df.groupby(["year", "fund_house"])["aum_crore"].sum().reset_index()

plt.figure(figsize=(16, 7))
ax = sns.barplot(
    data=aum_grouped, x="year", y="aum_crore",
    hue="fund_house", palette="tab20"
)

# Highlight SBI bars
for bar in ax.patches:
    if bar.get_height() >= 1250000:  # ~₹12.5L Cr
        bar.set_edgecolor("gold")
        bar.set_linewidth(2.5)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/100000:.1f}L Cr"))
plt.title("AUM Growth by Fund House (2022–2025)\n⭐ Gold border = SBI ₹12.5L Cr dominance")
plt.xlabel("Year")
plt.ylabel("AUM")
plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(CHARTS / "T2_aum_bar.png", dpi=150)
print("✅ T2 saved")
