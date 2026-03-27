import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 Crypto Reversal Scanner (Pressure + Bounce)")

COINS = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC"]

# =========================
def get_24h(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}-USD/candles"
    r = requests.get(url).json()

    if not isinstance(r, list) or len(r) < 24:
        return None

    df = pd.DataFrame(r, columns=[
        "time","low","high","open","close","volume"
    ])

    df = df.head(24).astype(float)
    return df

# =========================
def detect_reversal(df):
    current_price = df.iloc[0]["close"]

    high_24 = df["high"].max()
    low_24 = df["low"].min()

    # 1) ضغط (قريب من القاع)
    near_bottom = (current_price - low_24) / (high_24 - low_24 + 1e-9)

    # 2) ضغط بيع (عدد الشموع الحمراء)
    red_candles = (df["close"] < df["open"]).sum()

    # 3) شمعة ارتداد
    last_green = df.iloc[0]["close"] > df.iloc[0]["open"]

    # 4) ذيل سفلي (رفض قاع)
    last_wick = (df.iloc[0]["open"] - df.iloc[0]["low"]) > (df.iloc[0]["high"] - df.iloc[0]["close"])

    score = 0

    # ضغط هبوط
    if near_bottom < 0.25:
        score += 40

    # ضغط بيع
    if red_candles >= 15:
        score += 30

    # بداية ارتداد
    if last_green:
        score += 20

    # رفض قاع
    if last_wick:
        score += 10

    return score, near_bottom, red_candles

# =========================
results = []

if st.button("🚀 Scan Reversal Opportunities"):

    progress = st.progress(0)

    for i, coin in enumerate(COINS):

        df = get_24h(coin)

        if df is None:
            continue

        score, near_bottom, reds = detect_reversal(df)

        if score >= 60:   # فلتر قوي للإشارات
            results.append({
                "Symbol": coin,
                "Score": score,
                "Pressure_Level": round(near_bottom, 2),
                "Red_Candles": reds,
                "Current_Close": df.iloc[0]["close"]
            })

        progress.progress((i+1)/len(COINS))

    if results:
        df_res = pd.DataFrame(results).sort_values("Score", ascending=False)
        st.success("🔥 Potential Reversal Coins Found")
        st.dataframe(df_res)
    else:
        st.warning("❌ مفيش فرص ارتداد قوية حالياً")
