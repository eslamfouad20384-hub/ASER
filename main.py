import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Real Daily Candles OHLCV (No Binance)")

# =========================
# تحويل الاسم
# =========================
def coin_to_id(name):
    name = name.lower().strip()

    mapping = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "bnb": "binancecoin",
        "sol": "solana",
        "xrp": "ripple",
        "ada": "cardano",
        "doge": "dogecoin",
        "ltc": "litecoin"
    }

    return mapping.get(name, name)

# =========================
# جلب بيانات دقيقة
# =========================
def get_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"

    params = {
        "vs_currency": "usd",
        "days": 30,
        "interval": "hourly"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if "prices" not in data:
            return None, None

        prices = data["prices"]
        volumes = data["total_volumes"]

        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["volume"] = [v[1] for v in volumes]

        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date

        candles = []

        for d, group in df.groupby("date"):
            open_p = group["price"].iloc[0]
            close_p = group["price"].iloc[-1]
            high_p = group["price"].max()
            low_p = group["price"].min()
            vol = group["volume"].sum()

            candles.append({
                "date": d,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "close": close_p,
                "volume": vol
            })

        return candles, "✅ Success"

    except Exception as e:
        return None, f"❌ Error: {e}"

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
# UI
# =========================
coin = st.text_input("✍️ اكتب العملة (BTC / ETH / SOL)")

if st.button("🚀 Generate Candles"):

    coin_id = coin_to_id(coin)

    candles, status = get_data(coin_id)

    st.write("Status:", status)

    if not candles:
        st.error("❌ No data")
        st.stop()

    df = pd.DataFrame(candles)

    st.subheader("📊 Daily OHLCV Candles")
    st.dataframe(df)

    # RSI
    rsi_val = rsi(df["close"].values)

    st.subheader("📈 Analysis")
    st.write("RSI:", rsi_val)
    st.write("Last Close:", df["close"].iloc[-1])
