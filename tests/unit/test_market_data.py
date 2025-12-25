import helpers

from sim import *

def test_get_current_bar():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)

    assert md.current_bar(start) == Bar.from_row(md.df.iloc[0])

    assert md.current_bar(end) == Bar.from_row(md.df.iloc[-1])

def test_get_most_recent_bar():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)

    assert md.most_recent_bar(start) == None

    assert md.most_recent_bar(end) == Bar.from_row(md.df.iloc[-2])
