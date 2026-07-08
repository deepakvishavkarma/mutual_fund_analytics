from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RAW=ROOT/"data"/"raw"
PROCESSED=ROOT/"data"/"processed"
CHARTS=ROOT/"reports"/"charts"
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv(PROCESSED / "nav_history_clean.csv")
df["date"] = pd.to_datetime(df["date"])

# Filter 2022–2026
df = df[(df["date"] >= "2022-01-01") & (df["date"] <= "2026-12-31")]

fig = go.Figure()

for code in df["amfi_code"].unique():
    fund_df = df[df["amfi_code"] == code]
    name = fund_df["scheme_name"].iloc[0] if "scheme_name" in fund_df.columns else str(code)
    fig.add_trace(go.Scatter(
        x=fund_df["date"], y=fund_df["nav"],
        mode="lines", name=name, line=dict(width=1), opacity=0.7
    ))

# Highlight 2023 bull run
fig.add_vrect(x0="2023-01-01", x1="2023-12-31",
              fillcolor="green", opacity=0.07,
              annotation_text="2023 Bull Run", annotation_position="top left")

# Highlight 2024 correction
fig.add_vrect(x0="2024-09-01", x1="2024-12-31",
              fillcolor="red", opacity=0.07,
              annotation_text="2024 Correction", annotation_position="top left")

fig.update_layout(
    title="Daily NAV Trend — All 40 Schemes (2022–2026)",
    xaxis_title="Date", yaxis_title="NAV (₹)",
    template="plotly_white", height=600,
    legend=dict(font=dict(size=8))
)

fig.write_html(CHARTS / "T1_nav_trend.html")
fig.write_image(CHARTS / "T1_nav_trend.png", width=1400, height=600)
print("✅ T1 saved")
