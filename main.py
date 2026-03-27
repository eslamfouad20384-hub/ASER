import streamlit as st
import requests
import json
import os
import numpy as np
import pandas as pd

# =========================
# إعدادات
# =========================
st.set_page_config(layout="wide")
st.title("🚀 Crypto Rebound Scanner")

DATA_FILE = "coin_data.json"

# =========================
# جلب العملات
# =========================
def fetch_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    res = requests.get(url, params=params)
    return res.json()

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
    for c in coins:
        coin = c["symbol"].upper()

        if coin not in old_data:
            old_data[coin] = []

        old_data[coin].append({
            "price": c["current_price"],
            "volume": c["total_volume"],
            "change": c["price_change_percentage_24h"]
        })

        # نخلي آخر 60 شمعة فقط
        old_data[coin] = old_data[coin][-60:]

    return old_data

# =========================
# RSI بسيط
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
# كشف الإشارة
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
# تشغيل
# =========================
coins = fetch_coins()
data = load_data()
data = update_data(coins, data)
save_data(data)

# =========================
# تجهيز الجدول
# =========================
rows = []

for c in coins:
    symbol = c["symbol"].upper()
    history = data.get(symbol, [])

    prices = [x["price"] for x in history]
    volumes = [x["volume"] for x in history]

    rsi = calc_rsi(prices)

    change = c["price_change_percentage_24h"]

    signal = get_signal(change, rsi)

    rows.append([
        symbol,
        c["current_price"],
        c["total_volume"],
        round(rsi, 2),
        signal
    ])

df = pd.DataFrame(rows, columns=["Coin", "Price", "Volume", "RSI", "Signal"])

# ترتيب حسب الفرص
order = {
    "🟢 STRONG BUY": 0,
    "🟢 BUY": 1,
    "🟡 WAIT": 2,
    "⚪ NO TRADE": 3
}

df["sort"] = df["Signal"].map(order)
df = df.sort_values("sort").drop(columns=["sort"])

# =========================
# عرض
# =========================
st.dataframe(df, use_container_width=True)
