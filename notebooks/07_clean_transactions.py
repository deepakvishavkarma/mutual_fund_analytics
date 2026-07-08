from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

import pandas as pd

df = pd.read_csv(RAW / "08_investor_transactions.csv")
print("Original shape:", df.shape)

# Standardise transaction_type
type_map = {
    "sip": "SIP", "Sip": "SIP", "SIP": "SIP",
    "lumpsum": "Lumpsum", "Lump Sum": "Lumpsum", "LUMPSUM": "Lumpsum",
    "redemption": "Redemption", "Redeem": "Redemption", "REDEMPTION": "Redemption"
}
df["transaction_type"] = df["transaction_type"].str.strip().map(type_map)
print("Unmapped types:", df["transaction_type"].isnull().sum())

# Validate amount > 0
df = df[df["amount_inr"] > 0]

# Fix dates
df["transaction_date"] = pd.to_datetime(df["transaction_date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["transaction_date"])

# Check KYC
valid_kyc = ["KYC Verified", "KYC Pending", "KYC Rejected"]
print("KYC values found:\n", df["kyc_status"].value_counts())
print("Invalid KYC rows:", df[~df["kyc_status"].isin(valid_kyc)].shape[0])

df.to_csv(PROCESSED / "transactions_clean.csv", index=False)
print("Saved. Final shape:", df.shape)
