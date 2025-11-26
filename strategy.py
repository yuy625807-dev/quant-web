import time
import json
import ccxt
import pandas as pd
import requests

config = json.load(open("config.json","r"))

exchange = ccxt.okx({
    "apiKey": config["API_KEY"],
    "secret": config["API_SECRET"],
    "password": config["API_PASSPHRASE"]
})

def send_wechat(msg):
    if not config["WEBHOOK"]:
        print("No Webhook.")
        return
    requests.post(config["WEBHOOK"], json={"msgtype":"text","text":{"content":msg}})

def get_data():
    ohlcv = exchange.fetch_ohlcv("BTC/USDT", "15m", limit=100)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    return df

def rsi(series, n=14):
    delta = series.diff()
    gain = delta.where(delta>0, 0).rolling(n).mean()
    loss = (-delta.where(delta<0, 0)).rolling(n).mean()
    rs = gain/loss
    return 100 - (100/(1+rs))

def run_strategy():
    df = get_data()
    df["rsi"] = rsi(df["close"])
    last = df.iloc[-1]

    if last["rsi"] > 70:
        signal = "SELL"
    elif last["rsi"] < 30:
        signal = "BUY"
    else:
        signal = "NONE"

    send_wechat(f"信号：{signal}，RSI={last['rsi']:.2f}")
    print("策略执行：", signal)

while True:
    run_strategy()
    time.sleep(60)
