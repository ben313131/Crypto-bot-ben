import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from flask import Flask
import threading

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1375951141145411684/ERvineFGI3Nlp3bj7CdSaer_AymUNo8_7O4Hx6G27U9tflhaV_nPRcmDRj60cDSJu__c"

symbols = ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "XRP-USD", "TRX-USD", "DOGE-USD"]

def send_alert(name, symbol, price, rsi, msg):
    json_data = {
        "username": "Spidey Bot 🕷️",
        "avatar_url": "https://i.imgur.com/JJY2xXG.png",
        "content": f"**{name} ({symbol})**\nPrix: `{price}`\nRSI: `{rsi}`\n📊 **Signal détecté :** {msg}"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=json_data)

def analyze(symbol):
    data = yf.download(symbol, period="90d", interval="1d")
    if data.empty or len(data) < 50:
        return

    close = data["Close"]
    volume = data["Volume"]

    # RSI
    rsi = RSIIndicator(close).rsi().iloc[-1]

    # Moyennes Mobiles
    mm20 = close.rolling(window=20).mean().iloc[-1]
    mm50 = close.rolling(window=50).mean().iloc[-1]

    # Bollinger
    bb = BollingerBands(close)
    lower_bb = bb.bollinger_lband().iloc[-1]
    upper_bb = bb.bollinger_hband().iloc[-1]

    # MACD
    macd = MACD(close)
    macd_diff = macd.macd_diff().iloc[-1]

    # Analyse volume pour pump/dump
    vol_mean = volume[-20:].mean()
    vol_current = volume.iloc[-1]
    vol_ratio = vol_current / vol_mean

    # Conditions d’alerte
    price = round(close.iloc[-1], 4)
    name = symbol.replace("-USD", "")
    message = []

    if rsi < 30:
        message.append("💎 RSI bas (sous 30) - potentiel achat")
    elif rsi > 70:
        message.append("🚨 RSI haut (au-dessus de 70) - possible surachat")

    if price < lower_bb:
        message.append("📉 Prix sous la bande de Bollinger - survendu ?")
    elif price > upper_bb:
        message.append("📈 Prix au-dessus de la bande - suracheté ?")

    if price > mm20 and mm20 > mm50:
        message.append("📊 Tendance haussière confirmée (MM20 > MM50)")
    elif price < mm20 and mm20 < mm50:
        message.append("🔻 Tendance baissière confirmée (MM20 < MM50)")

    if macd_diff > 0:
        message.append("🟢 MACD haussier")
    elif macd_diff < 0:
        message.append("🔴 MACD baissier")

    if vol_ratio > 3:
        message.append("🚀 Volume X3 - activité inhabituelle")

    if message:
        send_alert(name, symbol, price, round(rsi, 2), "\n".join(message))

# Flask pour Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Spidey Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    while True:
        for symbol in symbols:
            try:
                analyze(symbol)
            except Exception as e:
                print(f"Erreur pour {symbol} : {e}")
        time.sleep(300)  # 1 fois par jour
if __name__ == "__main__":
    # ... ici, ton code habituel pour lancer le bot, comme app.run() si tu utilises Flask

    # TEST MANUEL D'ENVOI
    import requests

    webhook_url = "https://discord.com/api/webhooks/..."  # Mets ton vrai URL ici
    data = {
        "content": "✅ Ceci est un test manuel du Spidey Bot (fin du script)"
    }

    response = requests.post(webhook_url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Réponse de Discord: {response.text}")
