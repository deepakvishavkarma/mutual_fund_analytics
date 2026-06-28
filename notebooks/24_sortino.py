import pandas as pd
import numpy as np

df = pd.read_csv("C:/users/dell/mutual_fund_analytics/data/processed/daily_returns.csv")

RF_ANNUAL = 0.065
RF_DAILY  = RF_ANNUAL / 252

results = []

for code, group in df.groupby("amfi_code"):
    name = group["scheme_name"].iloc[0] \
           if "scheme_name" in group.columns else str(code)
    r = group["daily_return"].dropna()
    if len(r) < 30:
        continue

    excess        = r - RF_DAILY
    downside      = r[r < 0]                         # negative days only
    downside_std  = downside.std() * np.sqrt(252)    # annualised
    ann_excess    = excess.mean() * 252

    sortino = round(ann_excess / downside_std, 4) if downside_std > 0 else None

    results.append({
        "amfi_code":    code,
        "scheme_name":  name,
        "sortino_ratio": sortino,
        "downside_vol":  round(downside_std, 4),
    })

sortino_df = pd.DataFrame(results).sort_values("sortino_ratio", ascending=False)
sortino_df["sortino_rank"] = range(1, len(sortino_df) + 1)
sortino_df.to_csv("C:/users/dell/mutual_fund_analytics/data/processed/sortino_ratio.csv", index=False)

print("✅ Sortino Ratio Rankings:")
print(sortino_df[["scheme_name", "sortino_ratio", "sortino_rank"]].to_string(index=False))
