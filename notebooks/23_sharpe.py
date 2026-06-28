import pandas as pd
import numpy as np

df = pd.read_csv("C:/users/dell/mutual_fund_analytics/data/processed/daily_returns.csv")
df["date"] = pd.to_datetime(df["date"])

RF_ANNUAL = 0.065          # RBI repo rate proxy
RF_DAILY  = RF_ANNUAL / 252

results = []

for code, group in df.groupby("amfi_code"):
    name = group["scheme_name"].iloc[0] \
           if "scheme_name" in group.columns else str(code)
    r  = group["daily_return"].dropna()
    if len(r) < 30:
        continue
    excess = r - RF_DAILY
    sharpe = round((excess.mean() / r.std()) * np.sqrt(252), 4)
    results.append({
        "amfi_code":   code,
        "scheme_name": name,
        "sharpe_ratio": sharpe,
        "ann_return":  round(r.mean() * 252, 4),
        "ann_vol":     round(r.std() * np.sqrt(252), 4),
    })

sharpe_df = pd.DataFrame(results).sort_values("sharpe_ratio", ascending=False)
sharpe_df["sharpe_rank"] = range(1, len(sharpe_df) + 1)
sharpe_df.to_csv("C:/users/dell/mutual_fund_analytics/data/processed/sharpe_ratio.csv", index=False)

print("✅ Sharpe Ratio Rankings:")
print(sharpe_df[["scheme_name", "sharpe_ratio", "sharpe_rank"]].to_string(index=False))
