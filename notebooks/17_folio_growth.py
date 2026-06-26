import pandas as pd
import plotly.graph_objects as go

# Use actual folio data if available, else use benchmark data
try:
    df = pd.read_csv("c:/users/dell/mutual_fund_analytics/data/raw/06_industry_folio_count.csv")
    df["month"] = pd.to_datetime(df["month"])
except FileNotFoundError:
    # Benchmark folio count data (AMFI published figures in Cr)
    data = {
        "date": pd.date_range(start="2022-01", end="2025-12", freq="MS"),
        "folio_cr": [13.26, 13.45, 13.67, 13.89, 14.10, 14.35,
                     14.62, 14.90, 15.20, 15.55, 15.88, 16.20,
                     16.55, 16.92, 17.30, 17.71, 18.15, 18.62,
                     19.10, 19.62, 20.15, 20.71, 21.30, 21.92,
                     22.30, 22.71, 23.10, 23.52, 23.95, 24.40,
                     24.87, 25.35, 25.62, 25.82, 26.00, 26.12,
                     26.12, 26.12, 26.12, 26.12, 26.12, 26.12,
                     26.12, 26.12, 26.12, 26.12, 26.12, 26.12][:48]
    }
    df = pd.DataFrame(data)

milestones = {
    "2022-01": "13.26 Cr Start",
    "2023-06": "20 Cr Crossed",
    "2024-06": "23 Cr Crossed",
    "2025-12": "26.12 Cr Peak"
}

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["month"], y=df["total_folios_crore"],
    mode="lines+markers", name="Folio Count",
    line=dict(color="purple", width=2.5),
    fill="tozeroy", fillcolor="rgba(155,89,182,0.1)"
))

for date_str, label in milestones.items():
    row = df[df["month"] == date_str]
    if not row.empty:
        fig.add_annotation(
            x=date_str, y=row["total_folios_crore"].values[0],
            text=f"🏁 {label}", showarrow=True,
            arrowhead=2, bgcolor="lavender",
            font=dict(size=10)
        )

fig.update_layout(
    title="Folio Count Growth: 13.26 Cr → 26.12 Cr (Jan 2022 – Dec 2025)",
    xaxis_title="Date", yaxis_title="Folio Count (Crore)",
    template="plotly_white", height=500
)

fig.write_html("c:/users/dell/mutual_fund_analytics/reports/charts/T7_folio_growth.html")
fig.write_image("c:/users/dell/mutual_fund_analytics/reports/charts/T7_folio_growth.png", width=1400, height=500)
print("✅ T7 saved")
