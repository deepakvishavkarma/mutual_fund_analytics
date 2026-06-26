import requests
import pandas as pd
import time

schemes = {
    119551: "SBI Bluechip Direct",
    120503: "ICICI Pru Bluechip Direct",
    118632: "Nippon India Large Cap Direct",
    119092: "Axis Bluechip Direct",
    120841: "Kotak Bluechip Direct"
}

all_navs = []

for code, name in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["data"])
        df["scheme_code"] = code
        df["scheme_name"] = data["meta"]["scheme_name"]
        df["fund_house"] = data["meta"]["fund_house"]
        all_navs.append(df)
        print(f"✅ {name}: {len(df)} records fetched")
    else:
        print(f"❌ Failed for {name} ({code}): HTTP {response.status_code}")
    
    time.sleep(0.5)  # polite delay

# Combine and save
df_all = pd.concat(all_navs, ignore_index=True)
df_all.to_csv("C:/Users/Dell/mutual_fund_analytics/data/raw/bluechip_5funds_nav.csv", index=False)
print(f"\n✅ Combined dataset saved: {df_all.shape}")
print(df_all.groupby("scheme_name")["nav"].count())
