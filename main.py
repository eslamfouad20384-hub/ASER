import streamlit as st
import requests
import pandas as pd

st.title("📊 Daily Candle Builder (Coinbase Source)")

# =========================
# جلب بيانات ساعة وتحويلها ليوم
# =========================
def get_daily_candle(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol.upper()}-USDT/candles"

    params = {
        "granularity": 3600  # 1 hour
    }

    r = requests.get(url).json()

    # لو الرد مش list
    if not isinstance(r, list):
        return None

    # Coinbase بيرجع آخر الشموع بالعكس
    df = pd.DataFrame(r, columns=[
        "time","low","high","open","close","volume"
    ])

    if len(df) < 24:
        return None

    # ناخد آخر 24 ساعة ونرتبهم
    df = df.head(24)

    df = df.astype(float)

    candle = {
        "Symbol": symbol.upper(),
        "Open": df.iloc[-1]["open"],
        "High": df["high"].max(),
        "Low": df["low"].min(),
        "Close": df.iloc[0]["close"],
        "Volume": df["volume"].sum()
    }

    return candle

# =========================
symbol = st.text_input("اكتب العملة (BTC / ETH / SOL)")

if st.button("جلب شمعة اليوم"):
    data = get_daily_candle(symbol)

    if data:
        st.success("تم جلب شمعة اليوم")
        st.write(data)
    else:
        st.error("❌ مفيش بيانات أو العملة غير صحيحة")
