"""
Bluestock MF Capstone — Live NAV Fetcher
=========================================
Fetches live NAV for all 40 schemes from mfapi.in
Usage: python scripts/live_nav_fetch.py
Bonus B1: Schedule via cron — 0 20 * * 1-5 python scripts/live_nav_fetch.py
"""

from pathlib import Path
import pandas as pd
import requests
import time
import logging
import sys
from datetime import datetime

ROOT    = Path(__file__).resolve().parent.parent
RAW     = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(REPORTS / "nav_fetch.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

BASE_URL = "https://api.mfapi.in/mf"


def fetch_nav(amfi_code: int, retries: int = 3) -> pd.DataFrame | None:
    """Fetch NAV history for one scheme with retry logic."""
    url = f"{BASE_URL}/{amfi_code}"
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            df = pd.DataFrame(data["data"])
            df["amfi_code"]   = amfi_code
            df["scheme_name"] = data["meta"]["scheme_name"]
            df["fund_house"]  = data["meta"]["fund_house"]
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
            df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
            return df.dropna(subset=["date", "nav"])
        except requests.exceptions.RequestException as e:
            log.warning(f"  Attempt {attempt}/{retries} failed for {amfi_code}: {e}")
            time.sleep(2 ** attempt)
    return None


def fetch_all():
    # Read scheme codes from fund master
    master_path = RAW / "01_fund_master.csv"
    if not master_path.exists():
        log.error("01_fund_master.csv not found in data/raw/")
        sys.exit(1)

    master = pd.read_csv(master_path)
    codes  = master["amfi_code"].unique().tolist()
    log.info(f"Fetching NAV for {len(codes)} schemes...")

    all_data = []
    failed   = []

    for i, code in enumerate(codes, 1):
        df = fetch_nav(int(code))
        if df is not None:
            all_data.append(df)
            log.info(f"  [{i}/{len(codes)}] ✅ {code}: {len(df)} records")
        else:
            failed.append(code)
            log.warning(f"  [{i}/{len(codes)}] ❌ {code}: failed after retries")
        time.sleep(0.4)   # polite delay

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        out = RAW / f"live_nav_{datetime.today().strftime('%Y%m%d')}.csv"
        combined.to_csv(out, index=False)
        log.info(f"✅ Saved {combined.shape} → {out.name}")
    else:
        log.error("No data fetched.")

    if failed:
        log.warning(f"Failed codes ({len(failed)}): {failed}")


if __name__ == "__main__":
    fetch_all()
