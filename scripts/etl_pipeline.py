"""
Bluestock MF Capstone — ETL Pipeline (D1)
==========================================
Runs full pipeline: raw CSV → clean → MySQL
Usage: python scripts/etl_pipeline.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
import logging
import sys
import os

# ── Paths (no hard-coding) ─────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS   = ROOT / "reports"

REPORTS.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

# ── Logging ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(REPORTS / "etl.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)


# ── Step 1: Clean NAV ──────────────────────────────────
def clean_nav():
    log.info("Step 1: Cleaning nav_history...")
    try:
        df = pd.read_csv(RAW / "02_nav_history.csv")
        log.info(f"  Loaded: {df.shape}")

        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        dropped = df["date"].isna().sum()
        df = df.dropna(subset=["date"])
        if dropped:
            log.warning(f"  Dropped {dropped} unparseable dates")

        df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
        df["nav"] = df.groupby("amfi_code")["nav"].ffill()
        df = df.drop_duplicates(subset=["amfi_code", "date"])

        invalid = (df["nav"] <= 0).sum()
        df = df[df["nav"] > 0]
        if invalid:
            log.warning(f"  Removed {invalid} invalid NAV rows (nav <= 0)")

        out = PROCESSED / "nav_history_clean.csv"
        df.to_csv(out, index=False)
        log.info(f"  ✅ Saved {df.shape} → {out.name}")
        return df

    except FileNotFoundError:
        log.error("  ❌ 02_nav_history.csv not found in data/raw/")
        raise
    except Exception as e:
        log.error(f"  ❌ NAV cleaning failed: {e}")
        raise


# ── Step 2: Clean Transactions ─────────────────────────
def clean_transactions():
    log.info("Step 2: Cleaning investor_transactions...")
    try:
        df = pd.read_csv(RAW / "08_investor_transactions.csv")
        log.info(f"  Loaded: {df.shape}")

        # Standardise transaction_type
        type_map = {
            "sip": "SIP", "Sip": "SIP", "SIP": "SIP",
            "lumpsum": "Lumpsum", "Lump Sum": "Lumpsum", "LUMPSUM": "Lumpsum",
            "redemption": "Redemption", "Redeem": "Redemption", "REDEMPTION": "Redemption"
        }
        df["transaction_type"] = df["transaction_type"].str.strip().map(type_map)
        unmapped = df["transaction_type"].isna().sum()
        if unmapped:
            log.warning(f"  {unmapped} unmapped transaction_type values dropped")

        # Use correct amount column name
        amount_col = "amount_inr" if "amount_inr" in df.columns else "amount"
        df = df[df[amount_col] > 0]

        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"], dayfirst=True, errors="coerce"
        )
        df = df.dropna(subset=["transaction_date", "transaction_type"])

        # KYC validation
        valid_kyc = ["Verified", "KYC Verified", "Pending", "KYC Pending", "Rejected"]
        bad_kyc = (~df["kyc_status"].isin(valid_kyc)).sum()
        if bad_kyc:
            log.warning(f"  {bad_kyc} rows with unexpected kyc_status values")

        out = PROCESSED / "transactions_clean.csv"
        df.to_csv(out, index=False)
        log.info(f"  ✅ Saved {df.shape} → {out.name}")
        return df

    except FileNotFoundError:
        log.error("  ❌ 08_investor_transactions.csv not found in data/raw/")
        raise
    except Exception as e:
        log.error(f"  ❌ Transaction cleaning failed: {e}")
        raise


# ── Step 3: Clean Performance ──────────────────────────
def clean_performance():
    log.info("Step 3: Cleaning scheme_performance...")
    try:
        df = pd.read_csv(RAW / "07_scheme_performance.csv")
        log.info(f"  Loaded: {df.shape}")

        return_cols = [c for c in df.columns if "return" in c.lower()]
        for col in return_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            anomalies = df[(df[col] < -50) | (df[col] > 200)][col].count()
            if anomalies:
                log.warning(f"  {col}: {anomalies} anomalies (outside -50% to 200%)")

        expense_col = next((c for c in df.columns if "expense" in c.lower()), None)
        if expense_col:
            df[expense_col] = pd.to_numeric(df[expense_col], errors="coerce")
            out_of_range = ((df[expense_col] < 0.1) | (df[expense_col] > 2.5)).sum()
            if out_of_range:
                log.warning(f"  {expense_col}: {out_of_range} values outside 0.1–2.5% range")

        out = PROCESSED / "performance_clean.csv"
        df.to_csv(out, index=False)
        log.info(f"  ✅ Saved {df.shape} → {out.name}")
        return df

    except FileNotFoundError:
        log.error("  ❌ 07_scheme_performance.csv not found in data/raw/")
        raise
    except Exception as e:
        log.error(f"  ❌ Performance cleaning failed: {e}")
        raise


# ── Step 4: Load to MySQL ───────────────────────────────
def load_to_mysql():
    log.info("Step 4: Loading to MySQL...")
    try:
        from sqlalchemy import create_engine, text

        # Read credentials from environment — never hard-code
        user     = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "yourpassword")
        host     = os.getenv("MYSQL_HOST", "localhost")
        db       = os.getenv("MYSQL_DB", "mf_analytics")

        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}/{db}",
            connect_args={"connect_timeout": 10}
        )

        tables = [
            ("nav_history_clean.csv",  "fact_nav"),
            ("transactions_clean.csv", "fact_transactions"),
            ("performance_clean.csv",  "fact_performance"),
            ("fund_scorecard.csv",     "fact_scorecard"),
        ]

        for filename, tablename in tables:
            filepath = PROCESSED / filename
            if not filepath.exists():
                log.warning(f"  ⚠️  {filename} not found, skipping")
                continue
            df = pd.read_csv(filepath)
            df.to_sql(tablename, engine, if_exists="replace", index=False)
            count = pd.read_sql(
                text(f"SELECT COUNT(*) as n FROM {tablename}"), engine
            )["n"][0]
            match = "✅" if count == len(df) else "❌ MISMATCH"
            log.info(f"  {match}  {tablename}: CSV={len(df)} | DB={count}")

    except ImportError:
        log.error("  ❌ pymysql not installed. Run: pip install pymysql")
        raise
    except Exception as e:
        log.error(f"  ❌ MySQL load failed: {e}")
        log.info("  ℹ️  Tip: set MYSQL_USER / MYSQL_PASSWORD env vars")
        raise


# ── Main ───────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 55)
    log.info("  Bluestock MF ETL Pipeline Starting")
    log.info("=" * 55)

    try:
        clean_nav()
        clean_transactions()
        clean_performance()
        load_to_mysql()
        log.info("=" * 55)
        log.info("  ✅ ETL Pipeline Complete")
        log.info("=" * 55)
    except Exception as e:
        log.error(f"Pipeline aborted: {e}")
        sys.exit(1)
