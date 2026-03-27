import streamlit as st
import requests
import json
import os
import numpy as np
import pandas as pd

# =========================
# إعداد الصفحة
# =========================
st.set_page_config(layout="wide")
st.title("🚀 Crypto Rebound Scanner PRO")

DATA_FILE = "coin_data.json"

# =========================
# جلب البيانات
# =========================
def fetch_coins():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if not isinstance(data, list):
            return []

        return data

    except:
        return []

# =========================
# تحميل JSON
# =========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# =========================
# حفظ JSON
# =========================
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# =========================
# تحديث البيانات
# =========================
def update_data(coins, old_data):

    if not isinstance(coins, list):
        return old_data

    for c in coins:

        if not isinstance(c, dict):
            continue

        symbol = c.get("symbol")
        if not symbol:
            continue

        coin = symbol.upper()

        if coin not in old_data:
            old_data[coin] = []

        old_data[coin].append({
            "price": c.get("current_price", 0),
            "volume": c.get("total_volume", 0),
            "change": c.get("price_change_percentage_24h", 0)
        })

        old_data[coin] = old_data[coin][-60:]

    return old_data

# =========================
# RSI
# =========================
def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50

    prices = np.array(prices)
    deltas = np.diff(prices)

    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# Signal
# =========================
def get_signal(change, rsi):
    if change <= -5 and rsi < 30:
        return "🟢 STRONG BUY"
    elif change <= -3 and rsi < 40:
        return "🟢 BUY"
    elif rsi < 50:
        return "🟡 WAIT"
    else:
        return "⚪ NO TRADE"

# =========================
# تشغيل النظام
# =========================
coins = fetch_coins()
data = load_data()
data = update_data(coins, data)
save_data(data)

# =========================
# الجدول الرئيسي
# =========================
rows = []

for c in coins:
    symbol = c.get("symbol", "").upper()
    history = data.get(symbol, [])

    prices = [x["price"] for x in history]

    rsi = calc_rsi(prices)
    change = c.get("price_change_percentage_24h", 0)

    signal = get_signal(change, rsi)

    rows.append([
        symbol,
        c.get("current_price", 0),
        c.get("total_volume", 0),
        round(rsi, 2),
        signal
    ])

df = pd.DataFrame(rows, columns=["Coin", "Price", "Volume", "RSI", "Signal"])

order = {
    "🟢 STRONG BUY": 0,
    "🟢 BUY": 1,
    "🟡 WAIT": 2,
    "⚪ NO TRADE": 3
}

df["sort"] = df["Signal"].map(order)
df = df.sort_values("sort").drop(columns=["sort"])

st.subheader("📊 Market Scanner")
st.dataframe(df, use_container_width=True)

# =========================
# 🔍 DEBUG TOOL
# =========================
st.divider()
st.subheader("🔍 Debug Single Coin Tool")

coin_input = st.text_input("Enter coin name (bitcoin, ethereum, solana):")

if st.button("Load Coin"):
    if coin_input:

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": coin_input.lower(),
            "order": "market_cap_desc",
            "per_page": 1,
            "page": 1,
            "sparkline": False
        }

        res = requests.get(url, params=params)
        data_debug = res.json()

        st.write("Raw API Response:")
        st.json(data_debug)

        if isinstance(data_debug, list) and len(data_debug) > 0:
            c = data_debug[0]

            st.success("Coin loaded")

            st.write({
                "symbol": c.get("symbol"),
                "price": c.get("current_price"),
                "volume": c.get("total_volume"),
                "change": c.get("price_change_percentage_24h")
            })
        else:
            st.error("No data found")
