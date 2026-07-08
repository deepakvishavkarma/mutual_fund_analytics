"""
Bluestock MF Capstone — Performance Metrics (D4)
=================================================
Computes: Daily Returns, CAGR (trading-day adjusted),
Sharpe, Sortino, Alpha/Beta, Max Drawdown, Scorecard
Usage: python scripts/compute_metrics.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import logging
import sys

ROOT      = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
RAW       = ROOT / "data" / "raw"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

RF_ANNUAL = 0.065          # RBI repo rate proxy
RF_DAILY  = RF_ANNUAL / 252


def load_nav():
    df = pd.read_csv(PROCESSED / "nav_history_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    # Merge scheme names
    master = pd.read_csv(RAW / "01_fund_master.csv")[["amfi_code", "scheme_name"]]
    df = df.merge(master, on="amfi_code", how="left")
    return df.sort_values(["amfi_code", "date"])


def compute_daily_returns(df):
    log.info("Computing daily returns...")
    df = df.copy()
    df["daily_return"] = df.groupby("amfi_code")["nav"].pct_change()
    df = df.dropna(subset=["daily_return"])
    # Remove extreme outliers (>50% single-day move = data error)
    df = df[df["daily_return"].abs() <= 0.5]
    out = PROCESSED / "daily_returns.csv"
    df.to_csv(out, index=False)
    log.info(f"  ✅ Daily returns: {df.shape} → {out.name}")
    return df


def compute_cagr(df):
    """CAGR using actual trading days, not calendar days."""
    log.info("Computing CAGR (trading-day adjusted)...")
    end_date  = df["date"].max()
    results   = []

    for code, group in df.groupby("amfi_code"):
        name  = group["scheme_name"].iloc[0]
        nav   = group.set_index("date")["nav"].sort_index()

        def cagr(years):
            start_date = end_date - pd.DateOffset(years=years)
            window = nav[nav.index >= start_date]
            if len(window) < 5:
                return None
            n_trading = len(window)
            n_years   = n_trading / 252        # ← trading days, not calendar
            if window.iloc[0] <= 0:
                return None
            return round((window.iloc[-1] / window.iloc[0]) ** (1 / n_years) - 1, 4)

        results.append({
            "amfi_code":   code,
            "scheme_name": name,
            "cagr_1yr":    cagr(1),
            "cagr_3yr":    cagr(3),
            "cagr_5yr":    cagr(5),
        })

    out_df = pd.DataFrame(results).sort_values("cagr_3yr", ascending=False)
    out    = PROCESSED / "cagr_table.csv"
    out_df.to_csv(out, index=False)
    log.info(f"  ✅ CAGR table: {out_df.shape} → {out.name}")
    return out_df


def compute_sharpe(ret_df):
    log.info("Computing Sharpe ratio...")
    results = []
    for code, group in ret_df.groupby("amfi_code"):
        name = group["scheme_name"].iloc[0]
        r    = group["daily_return"].dropna()
        if len(r) < 30:
            continue
        excess = r - RF_DAILY
        sharpe = round((excess.mean() / r.std()) * np.sqrt(252), 4)
        results.append({
            "amfi_code":    code,
            "scheme_name":  name,
            "sharpe_ratio": sharpe,
            "ann_return":   round(r.mean() * 252, 4),
            "ann_vol":      round(r.std() * np.sqrt(252), 4),
        })
    out_df = pd.DataFrame(results).sort_values("sharpe_ratio", ascending=False)
    out_df["sharpe_rank"] = range(1, len(out_df) + 1)
    out = PROCESSED / "sharpe_ratio.csv"
    out_df.to_csv(out, index=False)
    log.info(f"  ✅ Sharpe: {out_df.shape} → {out.name}")
    return out_df


def compute_sortino(ret_df):
    log.info("Computing Sortino ratio...")
    results = []
    for code, group in ret_df.groupby("amfi_code"):
        name = group["scheme_name"].iloc[0]
        r    = group["daily_return"].dropna()
        if len(r) < 30:
            continue
        excess       = r - RF_DAILY
        downside     = r[r < 0]
        downside_std = downside.std() * np.sqrt(252)
        ann_excess   = excess.mean() * 252
        sortino = round(ann_excess / downside_std, 4) if downside_std > 0 else None
        results.append({
            "amfi_code":     code,
            "scheme_name":   name,
            "sortino_ratio": sortino,
            "downside_vol":  round(downside_std, 4),
        })
    out_df = pd.DataFrame(results).sort_values("sortino_ratio", ascending=False)
    out_df["sortino_rank"] = range(1, len(out_df) + 1)
    out = PROCESSED / "sortino_ratio.csv"
    out_df.to_csv(out, index=False)
    log.info(f"  ✅ Sortino: {out_df.shape} → {out.name}")
    return out_df


def compute_alpha_beta(ret_df):
    log.info("Computing Alpha & Beta (OLS)...")
    # Use equal-weight market proxy
    bench = ret_df.groupby("date")["daily_return"].mean().reset_index()
    bench.columns = ["date", "bench_return"]

    results = []
    for code, group in ret_df.groupby("amfi_code"):
        name   = group["scheme_name"].iloc[0]
        merged = group.merge(bench, on="date", how="inner").dropna()
        if len(merged) < 60:
            continue
        slope, intercept, r_val, p_val, _ = stats.linregress(
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
    out_df = pd.DataFrame(results).sort_values("alpha", ascending=False)
    out_df["alpha_rank"] = range(1, len(out_df) + 1)
    out = PROCESSED / "alpha_beta.csv"
    out_df.to_csv(out, index=False)
    log.info(f"  ✅ Alpha/Beta: {out_df.shape} → {out.name}")
    return out_df


def compute_max_drawdown(nav_df):
    log.info("Computing Max Drawdown...")
    results = []
    for code, group in nav_df.groupby("amfi_code"):
        name  = group["scheme_name"].iloc[0]
        g     = group.set_index("date")["nav"].sort_index()
        roll_max  = g.cummax()
        drawdown  = g / roll_max - 1
        max_dd    = drawdown.min()
        dd_end    = drawdown.idxmin()
        dd_start  = g[:dd_end].idxmax()
        results.append({
            "amfi_code":      code,
            "scheme_name":    name,
            "max_drawdown":   round(max_dd, 4),
            "drawdown_start": dd_start.date(),
            "drawdown_end":   dd_end.date(),
            "recovery_days":  (dd_end - dd_start).days,
        })
    out_df = pd.DataFrame(results).sort_values("max_drawdown")
    out_df["dd_rank"] = range(1, len(out_df) + 1)
    out = PROCESSED / "max_drawdown.csv"
    out_df.to_csv(out, index=False)
    log.info(f"  ✅ Max Drawdown: {out_df.shape} → {out.name}")
    return out_df


def compute_scorecard(cagr_df, sharpe_df, alpha_df, dd_df):
    log.info("Computing Fund Scorecard (0-100)...")
    perf_path = PROCESSED / "performance_clean.csv"
    perf = pd.read_csv(perf_path) if perf_path.exists() else None

    sc = cagr_df[["amfi_code", "scheme_name", "cagr_3yr"]].copy()
    sc = sc.merge(sharpe_df[["amfi_code", "sharpe_ratio"]], on="amfi_code", how="left")
    sc = sc.merge(alpha_df[["amfi_code", "alpha"]], on="amfi_code", how="left")
    sc = sc.merge(dd_df[["amfi_code", "max_drawdown"]], on="amfi_code", how="left")

    if perf is not None:
        expense_col = next((c for c in perf.columns if "expense" in c.lower()), None)
        if expense_col:
            sc = sc.merge(perf[["amfi_code", expense_col]].rename(
                columns={expense_col: "expense_ratio"}), on="amfi_code", how="left")
        else:
            sc["expense_ratio"] = 1.5
    else:
        sc["expense_ratio"] = 1.5

    n = len(sc)

    def norm_rank(series, ascending=False):
        rank = series.rank(ascending=ascending, na_option="bottom")
        return 100 * (1 - (rank - 1) / (n - 1))

    sc["score_return"]  = norm_rank(sc["cagr_3yr"],      ascending=False)
    sc["score_sharpe"]  = norm_rank(sc["sharpe_ratio"],   ascending=False)
    sc["score_alpha"]   = norm_rank(sc["alpha"],          ascending=False)
    sc["score_expense"] = norm_rank(sc["expense_ratio"],  ascending=True)   # lower = better
    sc["score_dd"]      = norm_rank(sc["max_drawdown"].abs(), ascending=True)  # lower = better

    sc["composite_score"] = (
        0.30 * sc["score_return"]  +
        0.25 * sc["score_sharpe"]  +
        0.20 * sc["score_alpha"]   +
        0.15 * sc["score_expense"] +
        0.10 * sc["score_dd"]
    ).round(2)

    sc = sc.sort_values("composite_score", ascending=False).reset_index(drop=True)
    sc["final_rank"] = range(1, n + 1)

    cols = ["final_rank", "amfi_code", "scheme_name", "composite_score",
            "cagr_3yr", "sharpe_ratio", "alpha", "expense_ratio", "max_drawdown"]
    out = PROCESSED / "fund_scorecard.csv"
    sc[cols].to_csv(out, index=False)
    log.info(f"  ✅ Scorecard: {sc.shape} → {out.name}")
    return sc


if __name__ == "__main__":
    log.info("=" * 55)
    log.info("  Bluestock MF — Performance Metrics")
    log.info("=" * 55)

    nav_df   = load_nav()
    ret_df   = compute_daily_returns(nav_df)
    cagr_df  = compute_cagr(nav_df)
    sharpe   = compute_sharpe(ret_df)
    sortino  = compute_sortino(ret_df)
    alpha_df = compute_alpha_beta(ret_df)
    dd_df    = compute_max_drawdown(nav_df)
    scorecard = compute_scorecard(cagr_df, sharpe, alpha_df, dd_df)

    log.info("=" * 55)
    log.info("  ✅ All metrics computed")
    log.info(f"\n  Top 5 Funds by Composite Score:")
    print(scorecard[["final_rank", "scheme_name", "composite_score"]].head(5).to_string(index=False))
