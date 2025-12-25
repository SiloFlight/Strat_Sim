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

class MarketData:
    df : pd.DataFrame

    def __init__(self, df) -> None:
        self.df = df

    def current_bar(self, ts : pd.Timestamp) -> Bar | None:
        new_df = self.df[self.df["start_ts"] <= ts]

        if len(new_df) == 0:
            return None
        else:
            return Bar.from_row(new_df.iloc[-1])

    def most_recent_bar(self, ts : pd.Timestamp) -> Bar | None:
        new_df = self.df[self.df["end_ts"] < ts]

        if len(new_df) == 0:
            return None
        else:
            return Bar.from_row(new_df.iloc[-1])