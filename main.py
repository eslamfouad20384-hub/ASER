import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 Crypto Recommendation Engine (BUY / WAIT / REJECT)")

COINS = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC"]

# =========================
def get_data(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}-USD/candles"
    r = requests.get(url).json()

    if not isinstance(r, list) or len(r) < 24:
        return None

    df = pd.DataFrame(r, columns=[
        "time","low","high","open","close","volume"
    ])

    return df.head(24).astype(float)

# =========================
def recommendation(df):

    close = df.iloc[0]["close"]
    open_ = df.iloc[0]["open"]

    high = df["high"].max()
    low = df["low"].min()

    volume = df["volume"].sum()

    # ضغط السعر
    pressure = (close - low) / (high - low + 1e-9)

    # سحب سيولة
    sweep = (df.iloc[0]["low"] <= low) and (close > low)

    # حجم قوي
    vol_avg = df["volume"].mean()
    volume_ok = df.iloc[0]["volume"] > vol_avg * 1.2

    # اتجاه
    trend_down = df.iloc[-1]["close"] < df.iloc[0]["close"]

    score = 0

    if pressure < 0.25:
        score += 30
    if sweep:
        score += 30
    if volume_ok:
        score += 20
    if trend_down:
        score += 10
    if close > open_:
        score += 10

    # =========================
    # القرار النهائي
    if score >= 75:
        signal = "🔥 شراء قوي"
    elif score >= 55:
        signal = "🟢 شراء"
    elif score >= 35:
        signal = "⏳ انتظار"
    else:
        signal = "❌ مرفوض"

    return signal, score

# =========================
results = []

if st.button("🚀 Run Recommendation Scan"):

    progress = st.progress(0)

    for i, coin in enumerate(COINS):

        df = get_data(coin)

        if df is None:
            continue

        signal, score = recommendation(df)

        results.append({
            "Symbol": coin,
            "Recommendation": signal,
            "Score": score,
            "Price": df.iloc[0]["close"]
        })

        progress.progress((i+1)/len(COINS))

    st.success("🔥 Done")

    st.dataframe(pd.DataFrame(results).sort_values("Score", ascending=False))
