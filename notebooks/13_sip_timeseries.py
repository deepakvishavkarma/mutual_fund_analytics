from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RAW=ROOT/"data"/"raw"
PROCESSED=ROOT/"data"/"processed"
CHARTS=ROOT/"reports"/"charts"
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv(PROCESSED / "transactions_clean.csv")
df["transaction_date"] = pd.to_datetime(df["transaction_date"])
df = df[df["transaction_type"] == "SIP"]

df["month"] = df["transaction_date"].dt.to_period("M").dt.to_timestamp()
monthly = df.groupby("month")["amount_inr"].sum().reset_index()
monthly.columns = ["month", "sip_inflow"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=monthly["month"], y=monthly["sip_inflow"],
    mode="lines+markers", name="SIP Inflow",
    line=dict(color="royalblue", width=2),
    fill="tozeroy", fillcolor="rgba(65,105,225,0.1)"
))

# Annotate all-time high Dec 2025
fig.add_annotation(
    x="2025-12-01", y=3100200000,
    text="🏆 All-Time High<br>₹31,002 Cr (Dec 2025)",
    showarrow=True, arrowhead=2,
    bgcolor="gold", font=dict(size=11, color="black")
)

fig.update_layout(
    title="Monthly SIP Inflow Trend (Jan 2022 – Dec 2025)",
    xaxis_title="Month", yaxis_title="SIP Inflow (₹)",
    template="plotly_white", height=500
)

fig.write_html(CHARTS / "T3_sip_trend.html")
fig.write_image(CHARTS / "T3_sip_trend.png", width=1400, height=500)
print("✅ T3 saved")
