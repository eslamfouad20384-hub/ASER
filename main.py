import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 STRICT Smart Reversal Scanner (High Quality Only)")

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
def smart_analyze(df):

    close = df.iloc[0]["close"]
    open_ = df.iloc[0]["open"]

    high = df["high"].max()
    low = df["low"].min()

    pressure = (close - low) / (high - low + 1e-9)

    sweep = (df.iloc[0]["low"] <= low) and (close > low)

    volume_now = df.iloc[0]["volume"]
    volume_avg = df["volume"].mean()

    volume_confirm = volume_now > volume_avg * 1.3

    trend_down = df.iloc[-1]["close"] < df.iloc[0]["close"]

    momentum = df["close"].head(3).mean() > df["close"].head(10).mean()

    score = 0

    if pressure < 0.20:
        score += 35

    if sweep:
        score += 30

    if volume_confirm:
        score += 25

    if trend_down:
        score += 5

    if momentum:
        score += 5

    # ================= STRICT FILTER
    if score >= 85:
        signal = "🔥 شراء قوي"
    elif score >= 70:
        signal = "🟢 شراء"
    else:
        signal = "❌ مرفوض"

    return signal, score

# =========================
results = []

if st.button("🚀 Run STRICT Scan"):

    coins = ["BTC","ETH","SOL","XRP","ADA","DOGE","AVAX","MATIC"]

    progress = st.progress(0)

    for i, coin in enumerate(coins):

        df = get_data(coin)

        if df is None:
            continue

        signal, score = smart_analyze(df)

        # 🔥 هنا الفلتر الحقيقي
        if signal != "❌ مرفوض":

            results.append({
                "Symbol": coin,
                "Signal": signal,
                "Score": score,
                "Price": df.iloc[0]["close"]
            })

        progress.progress((i+1)/len(coins))

    if results:
        st.success("🔥 High Quality Signals Only")
        st.dataframe(pd.DataFrame(results).sort_values("Score", ascending=False))
    else:
        st.warning("❌ No strong setups right now")
