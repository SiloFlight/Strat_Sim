from dataclasses import asdict

import pandas as pd
import pytest

import helpers

from sim import *

def test_get_current_bar():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)

    assert md.current_bar(start) == Bar.from_row(md.df.iloc[0])

    assert md.current_bar(end) == None

def test_get_most_recent_bar():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)

    assert md.most_recent_bar(start) == None

    assert md.most_recent_bar(end) == Bar.from_row(md.df.iloc[-2])

def test_validate():
    # Monotonicity Failure
    with pytest.raises(ValueError, match="strictly increasing"):
        md_1 = helpers.market_data.get_simple_market_data(5)

        df = pd.concat([md_1.df,md_1.df])

        MarketData(df)
    
    # Malformed Intervals
    with pytest.raises(ValueError,match="strictly less"):
        r1 = asdict(Bar(start_ts=pd.Timestamp("2000-01-01"),end_ts=pd.Timestamp("2000-01-01"),open=0,high=0,low=0,close=0,volume=0,trades=0,VWAP=0))

        MarketData(pd.DataFrame([r1]))

    # Non disjoint intervals
    with pytest.raises(ValueError,match="disjoint"):
        r1 = asdict(Bar(start_ts=pd.Timestamp("2000-01-01"),end_ts=pd.Timestamp("2000-01-03"),open=0,high=0,low=0,close=0,volume=0,trades=0,VWAP=0))
        r2 = asdict(Bar(start_ts=pd.Timestamp("2000-01-02"),end_ts=pd.Timestamp("2000-01-04"),open=0,high=0,low=0,close=0,volume=0,trades=0,VWAP=0))

        MarketData(pd.DataFrame([r1,r2]))

