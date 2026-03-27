import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 Full Market Smart Scanner (AI Filter)")

# =========================
# جلب كل العملات من Coinbase
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
# جلب بيانات
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
# فلترة ذكية قبل التحليل
# =========================
def smart_filter(df):

    volume = df["volume"].sum()
    volatility = (df["high"].max() - df["low"].min()) / df["close"].mean()

    # شروط الفلتر
    if volume < 1000:
        return False

    if volatility < 0.02:
        return False

    return True

# =========================
# التقييم النهائي
# =========================
def analyze(df):

    close = df.iloc[0]["close"]
    open_ = df.iloc[0]["open"]

    high = df["high"].max()
    low = df["low"].min()

    pressure = (close - low) / (high - low + 1e-9)

    sweep = (df.iloc[0]["low"] <= low) and (close > low)

    vol_ok = df.iloc[0]["volume"] > df["volume"].mean()

    trend_down = df.iloc[-1]["close"] < df.iloc[0]["close"]

    score = 0

    if pressure < 0.25:
        score += 30
    if sweep:
        score += 30
    if vol_ok:
        score += 20
    if trend_down:
        score += 10
    if close > open_:
        score += 10

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

if st.button("🚀 Scan Full Market"):

    coins = get_all_products()

    progress = st.progress(0)

    for i, coin in enumerate(coins):

        df = get_data(coin)

        if df is None:
            continue

        # فلتر ذكي الأول
        if not smart_filter(df):
            continue

        signal, score = analyze(df)

        if signal in ["🔥 شراء قوي", "🟢 شراء"]:

            results.append({
                "Symbol": coin,
                "Signal": signal,
                "Score": score,
                "Price": df.iloc[0]["close"]
            })

        progress.progress((i+1)/len(coins))

    if results:
        st.success("🔥 Smart Opportunities Found")
        st.dataframe(pd.DataFrame(results).sort_values("Score", ascending=False))
    else:
        st.warning("❌ No strong setups")
