import pandas as pd
import pytest

from sim import *

from helpers.broker import create_live_order

def test_handle_requests():
    delta = pd.Timedelta(days=1)
    broker = Broker(0,PerShareFee(0),delta)

    ts = pd.Timestamp("2000-01-01")

    order_request = OrderRequest(OrderSide.BUY,OrderType.MARKET,10)
    
    events = broker.handle_requests(ts,[order_request],[])

    assert len(events) == 1

    ev = events[0]

    assert isinstance(ev,OrderArrivesAtMarketEvent)
    assert ev.ts == ts + delta

    order_id = ev.order_submission.order_id

    cancellation_request = CancellationRequest(order_id)

    events = broker.handle_requests(ts,[],[cancellation_request])

    assert len(events) == 1

    ev = events[0]

    assert isinstance(ev,CancellationArrivesAtMarketEvent)
    assert ev.ts == ts + delta

def test_handle_fill():
    delta = pd.Timedelta(days=0)
    broker = Broker(100,PerShareFee(1),delta)

    order_qty = 10

    order_req = OrderRequest(OrderSide.BUY,OrderType.MARKET,order_qty)

    ts = pd.Timestamp("2000-01-01")

    order_id = create_live_order(broker,order_req,ts)

    assert order_id in broker.orders

    order = broker.orders[order_id]

    assert order.state == OrderState.LIVE
    assert order.remaining_quantity == order_qty

    with pytest.raises(ValueError,match="greater than remaining qty"):
        broker.handle_fill(Fill(order_id,order_qty+1,OrderSide.BUY,9,ts+2*delta))

    broker.handle_fill(Fill(order_id,9,OrderSide.BUY,9,ts+delta))

    assert order.state == OrderState.PARTIALLY_FILLED
    assert order.remaining_quantity == 1
    assert broker.portfolio.cash == 10
    assert broker.portfolio.position == 9

    broker.handle_fill(Fill(order_id,1,OrderSide.BUY,9,ts+2*delta))

    assert order.state == OrderState.FILLED
    assert order.remaining_quantity == 0
    assert broker.portfolio.cash == 0
    assert broker.portfolio.position == 10

    with pytest.raises(RuntimeError,match="nonexistent order"):
        broker.handle_fill(Fill(-1,1,OrderSide.BUY,9,ts+2*delta))

    


    