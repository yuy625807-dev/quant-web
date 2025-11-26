import json
import pandas as pd
import ccxt
from dash import Dash, html, dcc
import plotly.graph_objects as go
from flask import Flask

config = json.load(open("config.json","r"))

server = Flask(__name__)
app = Dash(__name__, server=server)

exchange = ccxt.okx({
    "apiKey": config["API_KEY"],
    "secret": config["API_SECRET"],
    "password": config["API_PASSPHRASE"]
})

def get_data():
    ohlcv = exchange.fetch_ohlcv("BTC/USDT", "15m", limit=200)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

df = get_data()

fig = go.Figure([go.Candlestick(
    x=df["time"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"]
)])

app.layout = html.Div([
    html.H1("量化交易可视化系统"),
    dcc.Graph(figure=fig)
])

server = app.server
