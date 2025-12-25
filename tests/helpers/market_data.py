import pandas as pd

from sim import *

def get_simple_market_data(n : int):

    delta = pd.Timedelta(minutes=1)

    df = pd.DataFrame([{
        "start_ts" : pd.Timestamp("2000-01-01") + i * delta,
        "end_ts" : pd.Timestamp("2000-01-01") + (i+1) * delta,
        "open" : i,
        "close" : i,
        "high" : i+1,
        "low" : i-1,
        "volume" : i,
        "trades" : i,
        "VWAP" : i
    } for i in range(n)])

    return MarketData(df)

def get_simple_market_data_with_ts(n : int):
    md = get_simple_market_data(n)

    return md, pd.Timestamp("2000-01-01"), pd.Timestamp("2000-01-01") + pd.Timedelta(minutes=1) * n
