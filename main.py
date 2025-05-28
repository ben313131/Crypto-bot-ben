
import time
import requests
import yfinance as yf
import pandas as pd
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

def calculate_macd(data):
    ema12 = data.ewm(span=12, adjust=False).mean()
    ema26 = data.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_bollinger_bands(data, window=20):
    sma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return upper_band, lower_band

def send_discord_alert(name, symbol, rsi, macd_signal, price, volume_alert):
    messages = []

    if rsi < 30:
        messages.append("ð **RSI en zone SURVENDUE**")
    elif rsi > 70:
        messages.append("ð¥ **RSI en zone SURACHETÃE**")

    if macd_signal:
        messages.append("ð **Croisement MACD haussier dÃ©tectÃ©**")

    if volume_alert:
        messages.append("â ï¸ **Volume anormalement Ã©levÃ© (pump/dump ?) dÃ©tectÃ©**")

    if messages:
        message = {
"content": f"**{name} ({symbol})**\nPrix actuel : ${price:.2f}\nRSI : {rsi:.2f}\n" + "\n".join(messages)
                       f"Prix actuel : ${price:.2f}
" +
                       f"RSI : {rsi:.2f}
" +
                       "
".join(messages)
        }
        requests.post(WEBHOOK_URL, json=message)

def check_market():
    for symbol, name in cryptos.items():
        data = yf.download(symbol, period="60d", interval="1d")
        if len(data) < 30:
            continue

        close = data["Close"]
        volume = data["Volume"]

        rsi = calculate_rsi(close).iloc[-1]
        macd, signal = calculate_macd(close)
        boll_upper, boll_lower = calculate_bollinger_bands(close)

        last_macd = macd.iloc[-1]
        prev_macd = macd.iloc[-2]
        last_signal = signal.iloc[-1]
        prev_signal = signal.iloc[-2]

        macd_bullish_cross = prev_macd < prev_signal and last_macd > last_signal

        avg_volume = volume.rolling(window=20).mean()
        volume_alert = volume.iloc[-1] > avg_volume.iloc[-1] * 2

        price = close.iloc[-1]

        send_discord_alert(name, symbol, rsi, macd_bullish_cross, price, volume_alert)

def run_bot():
    while True:
        print("[Spidey Bot] Analyse en cours...")
        check_market()
        time.sleep(300)

app = Flask(__name__)

@app.route('/')
def home():
    return "Spidey Bot est en ligne !"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_flask).start()
Thread(target=run_bot).start()
