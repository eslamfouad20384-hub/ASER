import streamlit as st
import requests
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Crypto Analyzer PRO (Safe Version)")

# =========================
# جلب كل العملات USDT (آمن 100%)
# =========================
@st.cache_data
def get_all_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        # حماية كاملة
        if not isinstance(data, dict) or "symbols" not in data:
            st.error("⚠️ API returned invalid data")
            return []

        symbols = []

        for s in data["symbols"]:
            if (
                s.get("status") == "TRADING"
                and s.get("quoteAsset") == "USDT"
            ):
                symbols.append(s["symbol"])

        return sorted(symbols)

    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return []

# تحميل العملات
coins = get_all_symbols()

if not coins:
    st.stop()

# =========================
# اختيار العملة
# =========================
coin = st.selectbox("📊 اختار العملة", coins)

# =========================
# جلب الشموع اليومية
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

        if not isinstance(data, list):
            return None

        candles = []

        for c in data:
            candles.append({
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5])
            })

        return candles

    except:
        return None

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
# تشغيل التحليل
# =========================
if st.button("🚀 Analyze"):

    candles = get_candles(coin)

    if not candles:
        st.error("❌ Failed to fetch candles")
        st.stop()

    closes = [c["close"] for c in candles]

    rsi_val = rsi(closes)

    last = candles[-1]
    prev = candles[-2]

    change = ((last["close"] - prev["close"]) / prev["close"]) * 100

    signal = get_signal(change, rsi_val)

    # =========================
    # عرض النتائج
    # =========================
    st.subheader("📊 RESULT")

    st.write("عملة:", coin)
    st.write("RSI:", rsi_val)
    st.write("Daily Change %:", change)
    st.write("Signal:", signal)

    if signal == "❌ NO DATA":
        st.error("❌ Fail")
    else:
        st.success("✅ Success")
