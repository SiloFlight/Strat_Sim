from dataclasses import dataclass

import pandas as pd

@dataclass
class Bar():
    start_ts : pd.Timestamp
    end_ts : pd.Timestamp
    open : float
    high : float
    low : float
    close : float
    volume : int
    trades : int
    VWAP : float

    @classmethod
    def from_row(cls,row : pd.Series):
        return Bar(start_ts=row["start_ts"],
                   end_ts=row["end_ts"],
                   open=row["open"],
                   high=row["high"],
                   low=row["low"],
                   close=row["close"],
                   volume=row["volume"],
                   trades=row["trades"],
                   VWAP=row["VWAP"])


"""
Market Data

Responsibilities
- Timestamp based reference to bars

Design Note - V1: current_bar implicitly returns final bar even after data is exhausted. MarketData assumed that df is sorted and disjoint temporally validation of that assumption is a future priority.
"""

class MarketDataSnapshot:
    df : pd.DataFrame

    def __init__(self, market_data : "MarketData", ts : pd.Timestamp) -> None:
        self.df = market_data.df[market_data.df["end_ts"] < ts]
    
    def current_bar(self, ts : pd.Timestamp):
        return MarketData.current_bar_from_df(self.df,ts)
    
    def most_recent_bar(self, ts : pd.Timestamp):
        return MarketData.most_recent_bar_from_df(self.df,ts)

class MarketData:
    df : pd.DataFrame

    def __init__(self, df) -> None:
        self.df = df
    
    @staticmethod
    def current_bar_from_df(df : pd.DataFrame, ts : pd.Timestamp):
        new_df = df[(df["start_ts"] <= ts) & (ts <  df["end_ts"])]

        if len(new_df) == 0:
            return None
        elif len(new_df) != 1:
            raise RuntimeError("Dataframe timestamps are not disjoint.")
        else:
            return Bar.from_row(new_df.iloc[-1])
    
    @staticmethod
    def most_recent_bar_from_df(df : pd.DataFrame, ts : pd.Timestamp):
        new_df = df[df["end_ts"] < ts]

        if len(new_df) == 0:
            return None
        else:
            return Bar.from_row(new_df.iloc[-1])

    def current_bar(self, ts : pd.Timestamp) -> Bar | None:
        return MarketData.current_bar_from_df(self.df,ts)

    def most_recent_bar(self, ts : pd.Timestamp) -> Bar | None:
        return MarketData.most_recent_bar_from_df(self.df,ts)
    
    def get_snapshot(self, ts : pd.Timestamp):
        return MarketDataSnapshot(self,ts)