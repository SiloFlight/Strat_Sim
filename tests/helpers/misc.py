import pandas as pd

def get_simple_ts(n : int = 0):
    return pd.Timestamp("2000-01-01")+ n * pd.Timedelta(minutes=1)