import pandas as pd

from sim import *
import helpers

def test_get_current_bar():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    delta = (end-start)/5
    latency = pd.Timedelta(minutes=0)
    S1 = "sym1"
    M1 = Market({S1 : md}, CappedFill(5), latency)

    ts = start + delta * 3

    snapshot = M1.get_snapshot(ts)

    assert snapshot.market_datas[S1].current_bar(ts) == None
    assert snapshot.market_datas[S1].current_bar(ts-delta) == Bar.from_row(md.df.iloc[2])

def test_get_most_recent_bar():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    delta = (end-start)/5
    latency = pd.Timedelta(minutes=0)
    S1 = "sym1"
    M1 = Market({S1 : md}, CappedFill(5), latency)

    ts = start + delta * 3

    snapshot = M1.get_snapshot(ts)

    assert snapshot.market_datas[S1].most_recent_bar(end) == Bar.from_row(md.df.iloc[2])


def test_get_symbols():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    latency = pd.Timedelta(minutes=0)
    S1,S2 = "sym1","sym2"
    M1 = Market({S1 : md, S2 : md}, CappedFill(5), latency)
    snapshot = M1.get_snapshot(end)

    assert set(snapshot.get_symbols()) == set([S1,S2])