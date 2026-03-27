import streamlit as st
import requests
import json
import os
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Full Crypto Analyzer (All Coins + Daily Data)")

DATA_FILE = "crypto_data.json"

# =========================
# جلب كل العملات USDT
# =========================
@st.cache_data
def get_all_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    data = requests.get(url).json()

    symbols = []

    for s in data["symbols"]:
        if s["status"] == "TRADING" and s["quoteAsset"] == "USDT":
            symbols.append(s["symbol"])

    return sorted(symbols)

coins = get_all_symbols()

# =========================
# اختيار العملة
# =========================
coin = st.selectbox("📊 اختار العملة", coins)

# =========================
# جلب الشموع اليومية
# =========================
def get_candles(symbol):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 60
    }

    res = requests.get(url, params=params)
    data = res.json()

    if not isinstance(data, list):
        return None, "❌ API Error"

    candles = []

    for c in data:
        candles.append({
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5])
        })

    return candles, "✅ Success"

# =========================
# RSI
# =========================
def calc_rsi(closes, period=14):
    prices = np.array(closes)

    if len(prices) < period + 1:
        return None

    diff = np.diff(prices)

    gain = np.where(diff > 0, diff, 0)
    loss = np.where(diff < 0, -diff, 0)

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# الإشارة
# =========================
def get_signal(change, rsi):
    if rsi is None:
        return "❌ NO DATA"

    if change < -5 and rsi < 30:
        return "🟢 STRONG BUY"
    elif change < -3:
        return "🟢 BUY"
    elif rsi < 50:
        return "🟡 WAIT"
    else:
        return "⚪ NO TRADE"

# =========================
# تشغيل التحليل
# =========================
if st.button("🚀 Analyze"):

    candles, status = get_candles(coin)

    st.write("Status:", status)

    if candles:

        closes = [c["close"] for c in candles]

        rsi_val = calc_rsi(closes)

        last = candles[-1]
        prev = candles[-2]

        change = ((last["close"] - prev["close"]) / prev["close"]) * 100

        signal = get_signal(change, rsi_val)

        # نجاح / فشل
        success = "✅ SUCCESS"

        # حفظ البيانات
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[coin] = {
            "rsi": rsi_val,
            "change": change,
            "signal": signal,
            "candles_count": len(candles),
            "status": success
        }

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

        # عرض النتائج
        st.subheader("📊 RESULT")

        st.write("عملة:", coin)
        st.write("RSI:", rsi_val)
        st.write("Daily Change %:", change)
        st.write("Signal:", signal)
        st.write("Status:", success)

        st.success("💾 Data saved successfully")

    else:
        st.error("❌ Failed to fetch data")
