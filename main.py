import streamlit as st
import requests
import pandas as pd

st.title("📊 Crypto Daily Candle Scanner")

# =========================
# جلب شمعة يوم (Daily Candle)
# =========================
def fetch_daily_candle(symbol):
    url = "https://min-api.cryptocompare.com/data/v2/histoday"

    params = {
        "fsym": symbol.upper(),
        "tsym": "USDT",
        "limit": 1   # آخر شمعة يوم فقط
    }

    r = requests.get(url).json()

    if "Data" not in r:
        return None

    data = r["Data"]["Data"]
    df = pd.DataFrame(data)

    candle = df.iloc[-1]

    return {
        "symbol": symbol.upper(),
        "open": candle["open"],
        "high": candle["high"],
        "low": candle["low"],
        "close": candle["close"],
        "volume": candle["volumeto"]
    }

# =========================
# UI
# =========================
symbol = st.text_input("اكتب اسم العملة (مثال BTC, ETH, SOL)")

if st.button("📈 جلب شمعة اليوم"):
    if symbol:
        data = fetch_daily_candle(symbol)

        if data:
            st.success(f"📊 شمعة يوم لـ {data['symbol']}")

            st.write("Open:", data["open"])
            st.write("High:", data["high"])
            st.write("Low:", data["low"])
            st.write("Close:", data["close"])
            st.write("Volume:", data["volume"])

        else:
            st.error("❌ فشل جلب البيانات")
