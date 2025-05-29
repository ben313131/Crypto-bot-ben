
import requests
import time
import pandas as pd
import ta
from datetime import datetime
from flask import Flask

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/TON_WEBHOOK_ICI"

symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "SOL/USDT", "XRP/USDT", "TRX/USDT", "DOGE/USDT"]
interval = "1d"

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.replace('/', '')}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume",
                                     "close_time", "quote_asset_volume", "number_of_trades",
                                     "taker_buy_base", "taker_buy_quote", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["close"] = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])
    return df

def analyze(symbol):
    df = get_klines(symbol, interval)
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
    df["macd_diff"] = ta.trend.MACD(close=df["close"]).macd_diff()
    bollinger = ta.volatility.BollingerBands(close=df["close"])
    df["bb_high"] = bollinger.bollinger_hband()
    df["bb_low"] = bollinger.bollinger_lband()
    df["bb_middle"] = bollinger.bollinger_mavg()

    latest = df.iloc[-1]
    rsi = latest["rsi"]
    macd_diff = latest["macd_diff"]
    close_price = latest["close"]
    volume = latest["volume"]
    name = symbol.split("/")[0]

    alerts = []

    if rsi < 30:
        alerts.append("ðµ **RSI bas** â Possible survente")
    elif rsi > 70:
        alerts.append("ð´ **RSI Ã©levÃ©** â Possible surachat")

    if macd_diff > 0:
        alerts.append("ð¢ **MACD haussier**")
    elif macd_diff < 0:
        alerts.append("ð» **MACD baissier**")

    if close_price < latest["bb_low"]:
        alerts.append("ð **Prix sous bande de Bollinger**")
    elif close_price > latest["bb_high"]:
        alerts.append("ð **Prix au-dessus de la bande de Bollinger**")

    if len(alerts) >= 2:
        send_alert(name, symbol, close_price, rsi, alerts)

def send_alert(name, symbol, price, rsi, messages):
    json_data = {
        "username": "Spidey Bot ð¤",
        "avatar_url": "https://i.imgur.com/1X9eU4g.png",
        "content": f"**{name} ({symbol})**\nPrix actuel : ${price:.2f}\nRSI : {rsi:.2f}\n" + "\n".join(messages)
    }
    requests.post(DISCORD_WEBHOOK_URL, json=json_data)

@app.route('/')
def home():
    return "Spidey Bot is running!"

if __name__ == "__main__":
    while True:
        for symbol in symbols:
            try:
                analyze(symbol)
            except Exception as e:
                print(f"Erreur pour {symbol} : {e}")
        time.sleep(86400)  # 1 jour = 86400 secondes
