from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RAW=ROOT/"data"/"raw"
PROCESSED=ROOT/"data"/"processed"
CHARTS=ROOT/"reports"/"charts"
import pandas as pd
import numpy as np

# Load all metric files
cagr    = pd.read_csv(PROCESSED / "cagr_table.csv")[["amfi_code", "scheme_name", "cagr_3yr"]]
sharpe  = pd.read_csv(PROCESSED / "sharpe_ratio.csv")[["amfi_code", "sharpe_ratio"]]
alpha   = pd.read_csv(PROCESSED / "alpha_beta.csv")[["amfi_code", "alpha", "beta"]]
dd      = pd.read_csv(PROCESSED / "max_drawdown.csv")[["amfi_code", "max_drawdown"]]

# Try to get expense ratio from performance data
try:
    perf = pd.read_csv(PROCESSED / "performance_clean.csv")[["amfi_code", "expense_ratio"]]
except:
    perf = pd.DataFrame({"amfi_code": cagr["amfi_code"], "expense_ratio": 1.5})

# Merge all
sc = cagr.merge(sharpe, on="amfi_code") \
         .merge(alpha,  on="amfi_code") \
         .merge(dd,     on="amfi_code") \
         .merge(perf,   on="amfi_code")

# Rank each metric (higher is better unless noted)
n = len(sc)

def rank_asc(series):
    # Higher value = better rank = lower number
    return series.rank(ascending=False)

def rank_desc(series):
    # Lower value = better rank (for expense ratio, drawdown)
    return series.rank(ascending=True)

sc["rank_return"]  = rank_asc(sc["cagr_3yr"])
sc["rank_sharpe"]  = rank_asc(sc["sharpe_ratio"])
sc["rank_alpha"]   = rank_asc(sc["alpha"])
sc["rank_expense"] = rank_desc(sc["expense_ratio"])   # lower expense = better
sc["rank_dd"]      = rank_desc(sc["max_drawdown"].abs())  # lower DD = better

# Normalise ranks to 0–100
def norm(rank_col):
    return 100 * (1 - (rank_col - 1) / (n - 1))

sc["score_return"]  = norm(sc["rank_return"])
sc["score_sharpe"]  = norm(sc["rank_sharpe"])
sc["score_alpha"]   = norm(sc["rank_alpha"])
sc["score_expense"] = norm(sc["rank_expense"])
sc["score_dd"]      = norm(sc["rank_dd"])

# Composite Score
sc["composite_score"] = (
    0.30 * sc["score_return"]  +
    0.25 * sc["score_sharpe"]  +
    0.20 * sc["score_alpha"]   +
    0.15 * sc["score_expense"] +
    0.10 * sc["score_dd"]
).round(2)

sc = sc.sort_values("composite_score", ascending=False).reset_index(drop=True)
sc["final_rank"] = range(1, len(sc) + 1)

cols = ["final_rank", "amfi_code", "scheme_name", "composite_score",
        "cagr_3yr", "sharpe_ratio", "alpha", "expense_ratio", "max_drawdown"]
sc[cols].to_csv(PROCESSED / "fund_scorecard.csv", index=False)

print("✅ Fund Scorecard (Top 10):")
print(sc[cols].head(10).to_string(index=False))
