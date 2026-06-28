import nbformat as nbf

nb    = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell(
    "# Performance Analytics — Mutual Fund Study\n"
    "**Author:** Devendra Parmar | **Date:** 2026\n\n"
    "Covers: Daily Returns, CAGR, Sharpe, Sortino, Alpha/Beta, Drawdown, Scorecard, Benchmark"
))

sections = [
    ("Daily Return Distribution",    "P0_daily_return_dist.png", "c:/users/dell/mutual_fund_analytics/data/processed/daily_returns.csv"),
    ("CAGR — 1yr / 3yr / 5yr",      None,                       "c:/users/dell/mutual_fund_analytics/data/processed/cagr_table.csv"),
    ("Sharpe Ratio Rankings",        None,                       "c:/users/dell/mutual_fund_analytics/data/processed/sharpe_ratio.csv"),
    ("Sortino Ratio Rankings",       None,                       "c:/users/dell/mutual_fund_analytics/data/processed/sortino_ratio.csv"),
    ("Alpha & Beta (OLS)",           None,                       "c:/users/dell/mutual_fund_analytics/data/processed/alpha_beta.csv"),
    ("Maximum Drawdown",             None,                       "c:/users/dell/mutual_fund_analytics/data/processed/max_drawdown.csv"),
    ("Fund Scorecard (0–100)",       None,                       "c:/users/dell/mutual_fund_analytics/data/processed/fund_scorecard.csv"),
    ("Benchmark Comparison",         "P7_benchmark.png",         None),
]

for title, chart, csv in sections:
    cells.append(nbf.v4.new_markdown_cell(f"## {title}"))
    code = "import pandas as pd\nfrom IPython.display import Image\n"
    if chart:
        code += f"Image('c:/users/dell/mutual_fund_analytics/reports/charts/{chart}', width=900)\n"
    if csv:
        code += f"pd.read_csv('{csv}').head(10)\n"
    cells.append(nbf.v4.new_code_cell(code))

nb.cells = cells
with open("c:/users/dell/mutual_fund_analytics/notebooks/Performance_Analytics.ipynb", "w") as f:
    nbf.write(nb, f)

print("✅ Performance_Analytics.ipynb created")
