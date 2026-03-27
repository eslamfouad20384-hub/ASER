import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 AI Daily Candle Builder (Binance Source)")

# =========================
# جلب شمعة يوم من 24 شمعة ساعة
# =========================
def get_daily_candle(symbol):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol.upper() + "USDT",
        "interval": "1h",
        "limit": 24
    }

    r = requests.get(url).json()

    # لو في error من Binance
    if isinstance(r, dict) and r.get("code"):
        return None

    df = pd.DataFrame(r, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","trades","tbb","tbq","ignore"
    ])

    # تحويل أرقام
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    # =========================
    # بناء شمعة اليوم
    # =========================
    candle = {
        "Symbol": symbol.upper(),
        "Open": df.iloc[0]["open"],
        "High": df["high"].max(),
        "Low": df["low"].min(),
        "Close": df.iloc[-1]["close"],
        "Volume": df["volume"].sum()
    }

    return candle

# =========================
# UI
# =========================
symbol = st.text_input("✍️ اكتب اسم العملة (BTC / ETH / SOL)")

if st.button("📈 جلب شمعة اليوم"):
    if not symbol:
        st.warning("اكتب اسم العملة الأول")
    else:
        data = get_daily_candle(symbol)

        if data:
            st.success(f"📊 شمعة يوم لـ {data['Symbol']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Open", data["Open"])
                st.metric("Low", data["Low"])

            with col2:
                st.metric("High", data["High"])

            with col3:
                st.metric("Close", data["Close"])
                st.metric("Volume", data["Volume"])

        else:
            st.error("❌ فشل جلب البيانات أو العملة غير صحيحة")
