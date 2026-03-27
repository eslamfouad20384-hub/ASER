import streamlit as st
import requests
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Manual Crypto Analyzer (Fixed & Safe)")

# =========================
# تصليح اسم العملة تلقائي
# =========================
def fix_symbol(name):
    name = name.upper().strip()

    # لو كتب BTC أو ETH فقط
    if name in ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "LTC"]:
        return name + "USDT"

    # لو بالفعل USDT موجود
    if "USDT" in name:
        return name

    # افتراضي
    return name + "USDT"

# =========================
# جلب الشموع
# =========================
def get_candles(symbol):
    url = "https://api.binance.com/api/v3/klines"

    try:
        params = {
            "symbol": symbol,
            "interval": "1d",
            "limit": 60
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # لو API رجع Error
        if isinstance(data, dict):
            return None, f"❌ API Error: {data.get('msg', 'Unknown error')}"

        if not isinstance(data, list):
            return None, "❌ Invalid response from API"

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

    except Exception as e:
        return None, f"❌ Request Error: {e}"

# =========================
# RSI
# =========================
def rsi(values, period=14):
    values = np.array(values)

    if len(values) < period + 1:
        return None

    diff = np.diff(values)

    gain = np.where(diff > 0, diff, 0)
    loss = np.where(diff < 0, -diff, 0)

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# Signal
# =========================
def get_signal(change, rsi_val):
    if rsi_val is None:
        return "❌ NO DATA"

    if change < -5 and rsi_val < 30:
        return "🟢 STRONG BUY"
    elif change < -3:
        return "🟢 BUY"
    elif rsi_val < 50:
        return "🟡 WAIT"
    else:
        return "⚪ NO TRADE"

# =========================
# UI
# =========================
coin = st.text_input("✍️ اكتب العملة (BTC / ETH / BTCUSDT)")

if st.button("🚀 Analyze"):

    if not coin:
        st.error("✍️ لازم تكتب عملة")
        st.stop()

    symbol = fix_symbol(coin)

    st.write("🔎 Symbol:", symbol)

    candles, status = get_candles(symbol)

    st.write("Status:", status)

    if not candles:
        st.error("❌ Failed to load candles")
        st.stop()

    closes = [c["close"] for c in candles]

    rsi_val = rsi(closes)

    last = candles[-1]
    prev = candles[-2]

    change = ((last["close"] - prev["close"]) / prev["close"]) * 100

    signal = get_signal(change, rsi_val)

    # =========================
    # النتائج
    # =========================
    st.subheader("📊 RESULT")

    st.write("عملة:", symbol)
    st.write("RSI:", rsi_val)
    st.write("Daily Change %:", change)
    st.write("Signal:", signal)

    st.success("✅ Done")
