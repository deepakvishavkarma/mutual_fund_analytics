import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell(
    "# EDA Key Findings — Mutual Fund Analytics\n"
    "**Project:** Indian Large-Cap Mutual Fund Analysis 2022–2026  \n"
    "**Author:** Deepak vishavkarma  \n"
    "**Date:** 2026"
))

findings = [
    ("Finding 1: NAV Growth Across Schemes",
     "All 40 large-cap schemes showed consistent NAV appreciation from 2022 to 2026, "
     "with average NAV growing ~68%, confirming long-term equity wealth creation.",
     "T1_nav_trend.png"),
    ("Finding 2: 2023 Bull Run Impact",
     "The 2023 bull run drove an average NAV increase of ~28% across all schemes, "
     "the highest single-year gain in the 4-year study period.",
     "T1_nav_trend.png"),
    ("Finding 3: SBI AUM Dominance",
     "SBI Mutual Fund maintained AUM leadership throughout 2022–2025, reaching 12.5L Cr "
     "and commanding ~18% of total industry AUM.",
     "T2_aum_bar.png"),
    ("Finding 4: SIP All-Time High",
     "Monthly SIP inflows reached an all-time high of 31,002 Cr in December 2025, "
     "reflecting growing retail investor participation.",
     "T3_sip_trend.png"),
    ("Finding 5: Equity Category Dominates Inflows",
     "Equity funds consistently received 60–70% of total monthly inflows, "
     "with Large-Cap and Flexi-Cap categories leading within equity.",
     "T4_category_heatmap.png"),
    ("Finding 6: Young Investors Drive SIP",
     "Investors aged 25–35 account for the highest SIP volumes, "
     "indicating strong financial awareness among millennials.",
     "T5_demographics.png"),
    ("Finding 7: Maharashtra & Gujarat Lead",
     "Maharashtra and Gujarat together contribute over 35% of total SIP inflows, "
     "reflecting T30 city concentration of mutual fund investments.",
     "T6_geographic.png"),
    ("Finding 8: Folio Count Doubled",
     "Total investor folios doubled from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025), "
     "indicating rapid mutual fund penetration across India.",
     "T7_folio_growth.png"),
    ("Finding 9: High NAV Correlation Within Large-Cap",
     "Pairwise correlation of daily returns among top 10 large-cap funds averaged 0.85+, "
     "suggesting similar portfolio construction and benchmark tracking.",
     "T8_correlation.png"),
    ("Finding 10: Financials & IT Dominate Portfolios",
     "Financial Services and IT together account for ~45% of aggregate sector allocation "
     "across all equity large-cap funds in the study.",
     "T9_sector_donut.png"),
]

for i, (title, insight, chart) in enumerate(findings, 1):
    cells.append(nbf.v4.new_markdown_cell(
        f"## {title}\n\n"
        f"**Insight:** {insight}\n\n"
        f"**Chart Reference:** `C:/users/dell/mutual_fund_analytics/reports/charts/{chart}`"
    ))
    cells.append(nbf.v4.new_code_cell(
        f"from IPython.display import Image\n"
        f"Image('C:/users/dell/mutual_fund_analytics/reports/charts/{chart}', width=900)"
    ))

nb.cells = cells
path = "C:/users/dell/mutual_fund_analytics/notebooks/T10_eda_findings.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"✅ Notebook saved: {path}")
