from dataclasses import dataclass
from typing import Tuple

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

class MarketDataSnapshot:
    df : pd.DataFrame

    def __init__(self, market_data : "MarketData", ts : pd.Timestamp) -> None:
        self.df = market_data.df[market_data.df["end_ts"] <= ts]
    
    def current_bar(self, ts : pd.Timestamp):
        return MarketData.current_bar_from_df(self.df,ts)
    
    def most_recent_bar(self, ts : pd.Timestamp):
        return MarketData.most_recent_bar_from_df(self.df,ts)

EXPECTED_COLUMNS = set(["start_ts","end_ts","open","high","low","close","volume","trades","VWAP"])

class MarketData:
    """
    Market Data

    Responsibilities
    - Timestamp based reference to bars
    """
    df : pd.DataFrame

    def __init__(self, df) -> None:
        validity,msg = MarketData.validate_df(df)
        if not validity:
            raise ValueError(f"Market Data constructed with invalid df : {msg}")
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
    
    @staticmethod
    def validate_df(df : pd.DataFrame) -> Tuple[bool,str]:
        if len(EXPECTED_COLUMNS-set(df.columns)) != 0:
            return False, "missing column(s)"
        
        timestamp_cols = ["start_ts","end_ts"]
        float_cols = ["open","high","low","close","VWAP"]
        int_cols = ["volume","trades"]

        # Datatype correctness

        for col in timestamp_cols:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                return False, f"invalid datetime column: {col}"
        
        for col in float_cols:
            if not pd.api.types.is_any_real_numeric_dtype(df[col]):
                print(df[col].dtype)
                return False, f"invalid float column: {col}"
        
        for col in int_cols:
            if not pd.api.types.is_integer_dtype(df[col]):
                return False, f"invalid integer column: {col}"
        
        # Timestamp monotonicity
        if not df["start_ts"].is_monotonic_increasing or df["start_ts"].duplicated().any():
            return False,"start_ts not strictly increasing"
        
        if not df["end_ts"].is_monotonic_increasing or df["end_ts"].duplicated().any():
            return False,"end_ts not strictly increasing"
        
        #Valid Bar Size
        if not (df["start_ts"] < df["end_ts"]).all():
            return False, "start_ts not strictly less than end_ts"

        # Timestamp disjointness
        if not (df["end_ts"].iloc[:-1].reset_index(drop=True) <= df["start_ts"].iloc[1:].reset_index(drop=True)).all():
            return False, "timestamps are not disjoint"
        
        return True,""

    def current_bar(self, ts : pd.Timestamp) -> Bar | None:
        return MarketData.current_bar_from_df(self.df,ts)

    def most_recent_bar(self, ts : pd.Timestamp) -> Bar | None:
        return MarketData.most_recent_bar_from_df(self.df,ts)
    
    def get_snapshot(self, ts : pd.Timestamp):
        return MarketDataSnapshot(self,ts)