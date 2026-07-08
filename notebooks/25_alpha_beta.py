from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RAW=ROOT/"data"/"raw"
PROCESSED=ROOT/"data"/"processed"
CHARTS=ROOT/"reports"/"charts"
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv(PROCESSED / "daily_returns.csv")
df["date"] = pd.to_datetime(df["date"])

# Load Nifty 100 benchmark returns
# Option A: if you have benchmark CSV
try:
    bench = pd.read_csv(RAW / "10_benchmark_indices.csv")
    bench["date"] = pd.to_datetime(bench["date"])
    bench = bench[["date", "close_value"]].rename(columns={"close_value": "bench_return"})
except FileNotFoundError:
    # Option B: compute from Nifty 100 NAV if available
    try:
        nifty = pd.read_csv(RAW / "10_benchmark_indices.csv")
        nifty["date"] = pd.to_datetime(nifty["date"])
        nifty = nifty.sort_values("date")
        nifty["bench_return"] = nifty["close"].pct_change()
        bench = nifty[["date", "bench_return"]].dropna()
    except FileNotFoundError:
        # Option C: simulate benchmark as equal-weight average of all funds
        print("No benchmark file found — using equal-weight proxy")
        bench = df.groupby("date")["daily_return"].mean().reset_index()
        bench.columns = ["date", "bench_return"]

results = []

for code, group in df.groupby("amfi_code"):
    name = group["scheme_name"].iloc[0] \
           if "scheme_name" in group.columns else str(code)

    merged = group.merge(bench, on="date", how="inner").dropna()
    if len(merged) < 60:
        continue

    slope, intercept, r_val, p_val, std_err = stats.linregress(
        merged["bench_return"], merged["daily_return"]
    )

    results.append({
        "amfi_code":   code,
        "scheme_name": name,
        "alpha":       round(intercept * 252, 4),   # annualised
        "beta":        round(slope, 4),
        "r_squared":   round(r_val ** 2, 4),
        "p_value":     round(p_val, 4),
    })

ab_df = pd.DataFrame(results).sort_values("alpha", ascending=False)
ab_df["alpha_rank"] = range(1, len(ab_df) + 1)
ab_df.to_csv(PROCESSED / "alpha_beta.csv", index=False)

print("✅ Alpha & Beta saved:")
print(ab_df[["scheme_name", "alpha", "beta", "r_squared"]].to_string(index=False))
