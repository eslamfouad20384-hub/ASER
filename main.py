import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Daily Candle Builder (From Hourly Data)")

# =========================
# جلب شمعة يوم من شمعات الساعة
# =========================
def get_daily_candle(symbol):
    url = "https://min-api.cryptocompare.com/data/v2/histohour"

    params = {
        "fsym": symbol.upper(),
        "tsym": "USDT",
        "limit": 24   # 24 ساعة = يوم كامل
    }

    r = requests.get(url).json()

    # تأمين الرد
    if r.get("Response") != "Success":
        return None

    data = r["Data"]["Data"]

    if not data or len(data) < 24:
        return None

    df = pd.DataFrame(data)

    candle = {
        "Symbol": symbol.upper(),
        "Open": df.iloc[0]["open"],
        "High": df["high"].max(),
        "Low": df["low"].min(),
        "Close": df.iloc[-1]["close"],
        "Volume": df["volumeto"].sum()
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

            st.metric("Open", data["Open"])
            st.metric("High", data["High"])
            st.metric("Low", data["Low"])
            st.metric("Close", data["Close"])
            st.metric("Volume", data["Volume"])

        else:
            st.error("❌ فشل جلب البيانات أو العملة غير صحيحة")
