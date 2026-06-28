import pandas as pd
import numpy as np
import plotly.graph_objects as go

df     = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/processed/nav_history_clean.csv")
scores = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/processed/fund_scorecard.csv")
df["date"] = pd.to_datetime(df["date"])

# Debug: print columns to confirm
print("Scorecard columns:", scores.columns.tolist())
print("NAV history columns:", df.columns.tolist())

# Safety check
if "amfi_code" not in scores.columns:
    print("❌ amfi_code missing from fund_scorecard.csv")
    print("Re-run P6_scorecard.py first, then run this script again")
    exit()

if "scheme_name" not in df.columns:
    print("⚠️ scheme_name not in nav history — using amfi_code as label")

# Top 5 fund codes from scorecard
top5 = scores.head(5)
top5_codes = top5["amfi_code"].tolist()
top5_names = top5["scheme_name"].tolist()

print(f"\nTop 5 funds selected: {top5_names}")

# 3-year window
end_date  = df["date"].max()
start     = end_date - pd.DateOffset(years=3)
df3       = df[
    (df["date"] >= start) &
    (df["amfi_code"].isin(top5_codes))
].copy()

if df3.empty:
    print("❌ No data found for top 5 funds in 3-year window")
    print("Check that amfi_codes in scorecard match nav_history")
    exit()

# Normalise NAV to 100 at start date
def normalise(group):
    group = group.sort_values("date").copy()
    first_nav = group["nav"].iloc[0]
    if first_nav == 0:
        group["nav_norm"] = 100
    else:
        group["nav_norm"] = group["nav"] / first_nav * 100
    return group

df3 = df3.groupby("amfi_code", group_keys=True).apply(normalise)

# Flatten multi-index and restore amfi_code as column
df3 = df3.reset_index(level=0)        # brings amfi_code back from index
df3 = df3.reset_index(drop=True)      # flatten row index
print("df3 columns after fix:", df3.columns.tolist())
print(df3.head(3))

print("df3 columns after normalise:", df3.columns.tolist())
print("df3 shape:", df3.shape)
print(df3.head(3))

# Plot
fig = go.Figure()
colors = ["royalblue", "darkorange", "green", "purple", "crimson"]

for i, code in enumerate(top5_codes):
    fund = df3[df3["amfi_code"] == code]
    if fund.empty:
        print(f"⚠️ No data for amfi_code {code} — skipping")
        continue
    label = str(top5_names[i])[:35] if i < len(top5_names) else str(code)
    fig.add_trace(go.Scatter(
        x=fund["date"],
        y=fund["nav_norm"],
        mode="lines",
        name=label,
        line=dict(width=2, color=colors[i % len(colors)])
    ))

# Load Nifty 50 benchmark
try:
    nifty50 = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/raw/10_benchmark_indices.csv")
    nifty50["date"] = pd.to_datetime(nifty50["date"])
    nifty50 = nifty50[nifty50["date"] >= start].sort_values("date").copy()
    first   = nifty50["close_value"].iloc[0]
    nifty50["nav_norm"] = nifty50["close_value"] / first * 100
    fig.add_trace(go.Scatter(
        x=nifty50["date"], y=nifty50["nav_norm"],
        mode="lines", name="Nifty 50",
        line=dict(width=2.5, color="black", dash="dash")
    ))
    print("✅ Nifty 50 benchmark added")

except FileNotFoundError:
    print("⚠️ nifty50_nav.csv not found — adding equal-weight proxy as benchmark")
    bench_proxy = df3.groupby("date")["nav_norm"].mean().reset_index()
    bench_proxy.columns = ["date", "nav_norm"]
    fig.add_trace(go.Scatter(
        x=bench_proxy["date"], y=bench_proxy["nav_norm"],
        mode="lines", name="Equal-Weight Proxy",
        line=dict(width=2.5, color="black", dash="dash")
    ))

fig.update_layout(
    title="Top 5 Funds vs Benchmark — 3-Year Normalised Performance (Base = 100)",
    xaxis_title="Date",
    yaxis_title="Normalised NAV (Base = 100)",
    template="plotly_white",
    height=550,
    legend=dict(font=dict(size=10))
)

fig.write_html("c:/users/dell/mutual_fund_analytics/reports/charts/P7_benchmark.html")
fig.write_image("c:/users/dell/mutual_fund_analytics/reports/charts/P7_benchmark.png", width=1400, height=550)
print("✅ Chart saved: c:/users/dell/mutual_fund_analytics/reports/charts/P7_benchmark.png")

# Tracking Error calculation
print("\n📊 Tracking Error (annualised):")
bench_returns = df3.groupby("date")["nav_norm"].mean().pct_change().dropna()

for i, code in enumerate(top5_codes):
    fund_nav = df3[df3["amfi_code"] == code].set_index("date")["nav_norm"]
    fund_ret = fund_nav.pct_change().dropna()
    aligned_fund, aligned_bench = fund_ret.align(bench_returns, join="inner")
    if len(aligned_fund) < 10:
        print(f"  ⚠️ Not enough data for {top5_names[i]}")
        continue
    te   = (aligned_fund - aligned_bench).std() * np.sqrt(252)
    name = str(top5_names[i])[:35]
    print(f"  {name}: TE = {te:.4f} ({te*100:.2f}%)")
