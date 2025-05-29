
import requests
import time
import yfinance as yf
from flask import Flask
import threading

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."  # Remplace par ton URL

symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD", "DOGE-USD", "TRX-USD"]

def rsi(prices, period=14):
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(deltas)):
        gain = gains[i]
        loss = losses[i]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

def send_alert(name, symbol, price, rsi_value):
    json_data = {
        "username": "Spidey Bot 🕷️",
        "avatar_url": "https://i.imgur.com/Uw6QZ5A.png",
        "content": f"**{name} ({symbol})**\nPrix: **{price:.2f} $**\nRSI: **{rsi_value:.2f}**"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=json_data)

def analyze(symbol):
    data = yf.download(symbol, period="1mo", interval="1d")
    close_prices = data["Close"].tolist()
    if len(close_prices) < 15:
        return

    current_price = close_prices[-1]
    rsi_value = rsi(close_prices)
    name = symbol.split("-")[0]

    if rsi_value < 30 or rsi_value > 70:
        send_alert(name, symbol, current_price, rsi_value)

# Serveur Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Spidey Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def start_bot():
    while True:
        for symbol in symbols:
            try:
                analyze(symbol)
            except Exception as e:
                print(f"Erreur pour {symbol} : {e}")
        time.sleep(86400)  # 1 jour

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    start_bot()
