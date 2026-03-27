import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("🚀 Ultra Smart Market Scanner (Strict AI Filter)")

# =========================
def get_all_products():
    url = "https://api.exchange.coinbase.com/products"
    r = requests.get(url).json()

    symbols = []
    for item in r:
        if item["quote_currency"] == "USD":
            symbols.append(item["base_currency"])

    return list(set(symbols))

# =========================
def get_data(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}-USD/candles"
    r = requests.get(url).json()

    if not isinstance(r, list) or len(r) < 72:
        return None

    df = pd.DataFrame(r, columns=[
        "time","low","high","open","close","volume"
    ])

    return df.head(72).astype(float)

# =========================
# 🔥 فلتر أقوى (مهم جدًا)
# =========================
def smart_filter(df):

    avg_volume = df["volume"].mean()
    total_volume = df["volume"].sum()

    price_range = df["high"].max() - df["low"].min()
    avg_price = df["close"].mean()

    volatility = price_range / (avg_price + 1e-9)

    # 🔴 فلتر حجم أقوى
    if avg_volume < 5000:
        return False

    # 🔴 لازم حركة حقيقية مش سوق ميت
    if volatility < 0.03:
        return False

    # 🔴 منع الشموع الضعيفة
    if df.iloc[0]["volume"] < avg_volume * 0.8:
        return False

    return True

# =========================
def analyze(df):

    close = df.iloc[0]["close"]
    open_ = df.iloc[0]["open"]

    high = df["high"].max()
    low = df["low"].min()

    pressure = (close - low) / (high - low + 1e-9)

    sweep = (df.iloc[0]["low"] <= low)

    volume_confirm = df.iloc[0]["volume"] > df["volume"].mean() * 1.2

    trend = df["close"].iloc[:10].mean() > df["close"].iloc[20:40].mean()

    momentum = close > df["close"].iloc[1:5].mean()

    score = 0

    # 🔥 شروط أقوى
    if pressure < 0.18:
        score += 35

    if sweep:
        score += 20

    if volume_confirm:
        score += 25

    if trend:
        score += 15

    if momentum:
        score += 10

    # ================= STRICT OUTPUT
    if score >= 85:
        signal = "🔥 شراء قوي جدًا"
    elif score >= 70:
        signal = "🟢 شراء قوي"
    elif score >= 55:
        signal = "⏳ انتظار"
    else:
        signal = "❌ مرفوض"

    return signal, score

# =========================
results = []

if st.button("🚀 Scan Full Market"):

    coins = get_all_products()

    progress = st.progress(0)

    for i, coin in enumerate(coins):

        df = get_data(coin)

        if df is None:
            continue

        if not smart_filter(df):
            continue

        signal, score = analyze(df)

        # 🔥 نسمح فقط بالقوي جدًا
        if score >= 75:

            results.append({
                "Symbol": coin,
                "Signal": signal,
                "Score": score,
                "Price": df.iloc[0]["close"]
            })

        progress.progress((i+1)/len(coins))

    if results:
        st.success("🔥 HIGH QUALITY SETUPS ONLY")
        st.dataframe(pd.DataFrame(results).sort_values("Score", ascending=False))
    else:
        st.warning("❌ No strong setups right now")
