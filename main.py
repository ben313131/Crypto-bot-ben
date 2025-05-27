
import time
import requests
import yfinance as yf
from flask import Flask
from threading import Thread

WEBHOOK_URL = "https://discord.com/api/webhooks/1375951141145411684/ERvineFGI3Nlp3bj7CdSaer_AymUNo8_7O4Hx6G27U9tflhaV_nPRcmDRj60cDSJu__c"

cryptos = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "ADA-USD": "Cardano",
    "SOL-USD": "Solana",
    "XRP-USD": "XRP",
    "TRX-USD": "TRON",
    "DOGE-USD": "Dogecoin"
}

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def send_discord_alert(name, symbol, rsi, price):
    if rsi < 30:
        condition = "💎 **SURVENDU** 💎"
    elif rsi > 70:
        condition = "🔥 **SURACHETÉ** 🔥"
    else:
        return

    message = {
        "content": f"{condition} - {name} ({symbol})
RSI: {rsi:.2f}
Prix actuel: ${price:.2f}"
    }
    requests.post(WEBHOOK_URL, json=message)

def check_market():
    for symbol, name in cryptos.items():
        data = yf.download(symbol, period="15m", interval="1m")
        if len(data) < 15:
            continue
        close_prices = data["Close"]
        rsi = calculate_rsi(close_prices).iloc[-1]
        price = close_prices.iloc[-1]
        send_discord_alert(name, symbol, rsi, price)

def run_bot():
    while True:
        print("[Spidey Bot] Analyse en cours...")
        check_market()
        time.sleep(300)  # 5 minutes

# Flask pour Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Spidey Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Threads
Thread(target=run_flask).start()
Thread(target=run_bot).start()
