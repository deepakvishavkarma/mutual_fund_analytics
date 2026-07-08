from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RAW=ROOT/"data"/"raw"
PROCESSED=ROOT/"data"/"processed"
CHARTS=ROOT/"reports"/"charts"
import pandas as pd
import numpy as np

df = pd.read_csv(PROCESSED / "nav_history_clean.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["amfi_code", "date"])

end_date   = df["date"].max()
start_1yr  = end_date - pd.DateOffset(years=1)
start_3yr  = end_date - pd.DateOffset(years=3)
start_5yr  = end_date - pd.DateOffset(years=5)

results = []

for code, group in df.groupby("amfi_code"):
    group = group.set_index("date")["nav"]
    name  = df[df["amfi_code"] == code]["scheme_name"].iloc[0] \
            if "scheme_name" in df.columns else str(code)

    def get_cagr(start_date, n_years):
        past = group[group.index >= start_date]
        if len(past) < 5:
            return None
        nav_start = past.iloc[0]
        nav_end   = past.iloc[-1]
        if nav_start <= 0:
            return None
        return round((nav_end / nav_start) ** (1 / n_years) - 1, 4)

    results.append({
        "amfi_code":   code,
        "scheme_name": name,
        "cagr_1yr":    get_cagr(start_1yr, 1),
        "cagr_3yr":    get_cagr(start_3yr, 3),
        "cagr_5yr":    get_cagr(start_5yr, 5),
    })

cagr_df = pd.DataFrame(results).sort_values("cagr_3yr", ascending=False)
cagr_df.to_csv(PROCESSED / "cagr_table.csv", index=False)

print("✅ CAGR Table:")
print(cagr_df.to_string(index=False))
