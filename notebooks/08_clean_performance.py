from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

import pandas as pd

df = pd.read_csv(RAW / "07_scheme_performance.csv")
print("Original shape:", df.shape)

return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]

# Force numeric
for col in return_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Flag anomalies
for col in return_cols:
    if col in df.columns:
        bad = df[(df[col] < -50) | (df[col] > 100)]
        print(f"{col} anomalies: {len(bad)} rows")

# Validate expense_ratio
if "expense_ratio" in df.columns:
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    out = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    print(f"Expense ratio out of range: {len(out)} rows")

df.to_csv(PROCESSED / "performance_clean.csv", index=False)
print("Saved. Final shape:", df.shape)
