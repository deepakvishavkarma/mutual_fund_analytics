import pandas as pd
import numpy as np

df = pd.read_csv("C:/users/dell/mutual_fund_analytics/data/processed/nav_history_clean.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["amfi_code", "date"])

results = []

for code, group in df.groupby("amfi_code"):
    name = group["scheme_name"].iloc[0] \
           if "scheme_name" in group.columns else str(code)

    group = group.set_index("date")["nav"]
    rolling_max = group.cummax()
    drawdown    = group / rolling_max - 1

    max_dd      = drawdown.min()
    dd_end_date = drawdown.idxmin()

    # Find start of this drawdown (last peak before end date)
    peak_before = group[:dd_end_date]
    dd_start_date = peak_before.idxmax()

    results.append({
        "amfi_code":      code,
        "scheme_name":    name,
        "max_drawdown":   round(max_dd, 4),
        "drawdown_start": dd_start_date.date(),
        "drawdown_end":   dd_end_date.date(),
        "recovery_days":  (dd_end_date - dd_start_date).days,
    })

dd_df = pd.DataFrame(results).sort_values("max_drawdown")
dd_df["dd_rank"] = range(1, len(dd_df) + 1)   # lower DD = better rank
dd_df.to_csv("C:/users/dell/mutual_fund_analytics/data/processed/max_drawdown.csv", index=False)

print("✅ Maximum Drawdown:")
print(dd_df[["scheme_name", "max_drawdown", "drawdown_start", "drawdown_end"]].to_string(index=False))
