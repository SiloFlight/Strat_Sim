import pandas as pd

from sim import *
import helpers

def test_order_arrival():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    latency = pd.Timedelta(minutes=0)
    symbol = "sym1"
    market = Market({symbol : md}, CappedFill(5), latency)

    order_submission = OrderSubmission(order_id=0,side=OrderSide.BUY,qty=5,symbol=symbol,order_type=OrderType.MARKET)

    events = market.handle_order_arrival(start,order_submission)

    assert len(events) == 1
    
    ev = events[0]
    
    assert isinstance(ev,FillArrivesAtBrokerEvent)
    assert ev.ts == start + latency
    assert ev.fill.qty == 5
    assert ev.fill.ts == start
    assert ev.fill.fill_price == Bar.from_row(md.df.iloc[0]).open
    assert market.order_infos[0].remaining_qty == 0

def test_market_update():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    latency = pd.Timedelta(minutes=0)
    symbol = "sym1"
    M1 = Market({symbol : md}, CappedFill(10), latency)

    order_submission = OrderSubmission(order_id=0,side=OrderSide.BUY,qty=10,symbol=symbol,order_type=OrderType.MARKET)

    M1.handle_order_arrival(start,order_submission)

    assert M1.order_infos[0].remaining_qty == 0

def test_cancellation_pre_fill():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    latency = pd.Timedelta(minutes=0)
    symbol = "sym1"
    M1 = Market({symbol : md}, CappedFill(5), latency)

    order_id = 0

    order_submission = OrderSubmission(order_id=order_id,side=OrderSide.BUY,qty=10,symbol=symbol,order_type=OrderType.MARKET)
    cancellation_submission = CancellationSubmission(order_id)

    cancellation_events = M1.handle_cancellation_arrival(start,cancellation_submission)

    assert len(cancellation_events) == 1
    assert isinstance(cancellation_events[0],CancellationArrivesAtBrokerEvent)
    assert order_id in M1.cancelled_orders
    assert cancellation_events[0].cancellation_result.cancellation_outcome == CancellationOutcome.CANCELLED

    order_events = M1.handle_order_arrival(start,order_submission)

    assert len(order_events) == 0

def test_cancellation_post_fill():
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(5)
    latency = pd.Timedelta(minutes=0)
    symbol = "sym1"
    M1 = Market({symbol : md}, CappedFill(10), latency)

    order_id = 0

    order_submission = OrderSubmission(order_id=order_id,side=OrderSide.BUY,qty=10,symbol=symbol,order_type=OrderType.MARKET)
    cancellation_submission = CancellationSubmission(order_id)

    M1.handle_order_arrival(start,order_submission)

    assert M1.order_infos[order_id].remaining_qty == 0

    cancellation_events = M1.handle_cancellation_arrival(start,cancellation_submission)

    assert len(cancellation_events) == 1
    assert isinstance(cancellation_events[0],CancellationArrivesAtBrokerEvent)
    assert order_id in M1.cancelled_orders
    assert cancellation_events[0].cancellation_result.cancellation_outcome == CancellationOutcome.NO_OP