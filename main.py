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

# Webhook Discord
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1375951141145411684/ERvineFGI3Nlp3bj7CdSaer_AymUNo8_7O4Hx6G27U9tflhaV_nPRcmDRj60cDSJu__c"

# Cryptos à surveiller
symbols = ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "XRP-USD", "TRX-USD", "DOGE-USD"]

# Fonction d'envoi sur Discord
def send_alert(name, symbol, price, rsi, msg):
    json_data = {
        "username": "Spidey Bot 🕷️",
        "avatar_url": "https://i.imgur.com/JJY2xXG.png",
        "content": f"**{name} ({symbol})**\nPrix: `{price}`\nRSI: `{rsi}`\n📊 **Signal détecté :** {msg}"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=json_data)
    print(f"[Discord] Statut : {response.status_code}")

# Analyse technique
def analyze(symbol):
    data = yf.download(symbol, period="90d", interval="1d")
    if data.empty or len(data) < 50:
        return

    close = data["Close"]
    volume = data["Volume"]

    # Indicateurs techniques
    rsi = RSIIndicator(close).rsi().iloc[-1]
    mm20 = close.rolling(window=20).mean().iloc[-1]
    mm50 = close.rolling(window=50).mean().iloc[-1]
    bb = BollingerBands(close)
    lower_bb = bb.bollinger_lband().iloc[-1]
    upper_bb = bb.bollinger_hband().iloc[-1]
    macd = MACD(close)
    macd_diff = macd.macd_diff().iloc[-1]
    vol_mean = volume[-20:].mean()
    vol_current = volume.iloc[-1]
    vol_ratio = vol_current / vol_mean

    # Conditions de signal
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

# Flask (interface simple pour Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "Spidey Bot is running!"

@app.route("/test")
def test_webhook():
    test_data = {
        "username": "Spidey Bot 🕷️",
        "avatar_url": "https://i.imgur.com/JJY2xXG.png",
        "content": "🧪 Ceci est un test manuel depuis la route `/test`"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=test_data)
    return "✅ Message de test envoyé sur Discord."

# Lancement de Flask dans un thread
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Lancement principal
if __name__ == "__main__":
    # Démarrer le serveur Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Test d'envoi au démarrage
    test_data = {
        "username": "Spidey Bot 🕷️",
        "avatar_url": "https://i.imgur.com/JJY2xXG.png",
        "content": "✅ Démarrage du Spidey Bot confirmé ! (Test automatique)"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=test_data)
    print(f"Test au démarrage : Status {response.status_code}")

    # Boucle principale (toutes les 5 minutes)
    while True:
        for symbol in symbols:
            try:
                analyze(symbol)
            except Exception as e:
                print(f"Erreur pour {symbol} : {e}")
        time.sleep(300)  # 5 minutes
