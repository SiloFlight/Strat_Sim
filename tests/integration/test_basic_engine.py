from typing import List, Tuple

import pandas as pd

from sim import *
import helpers
from sim import CancellationRequest, OrderRequest

class Strat(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0

    def run(self) -> Tuple[List[OrderRequest], List[CancellationRequest]]:
        if self.step == 0:
            self.step += 1

            order_req_1 = OrderRequest(OrderSide.BUY,OrderType.MARKET,5)
            order_req_2 = OrderRequest(OrderSide.BUY,OrderType.MARKET,10)
            
            return [order_req_1,order_req_2],[]
        else:
            cancel_req = CancellationRequest(1)
            return [],[cancel_req]

def test_engine_order_cancellation_flow():
    delta = pd.Timedelta(minutes=1)
    strategy = Strat()
    broker = Broker(100,PerShareFee(2),delta*2)
    md,start,end = helpers.market_data.get_simple_market_data_with_ts(10)

    market = Market(md,CappedFill(5),delta*2)

    engine = Engine(strategy,broker,market)

    engine.insert_event(RunStrategyEvent(EventType.RUN_STRATEGY,start))
    engine.insert_event(RunStrategyEvent(EventType.RUN_STRATEGY,start + 5 * delta))

    engine.insert_event(UpdateMarketDataEvent(EventType.UPDATE_MARKET_DATA,start + 7 * delta))

    engine.run()

    assert len(broker.orders) == 2

    O1,O2 = broker.orders[0],broker.orders[1]

    print(O1.fills,O2.fills)

    assert broker.portfolio.cash == 60
    assert broker.portfolio.position == 10   
    
    assert O1.state == OrderState.FILLED
    assert O2.state == OrderState.CANCELLED

    assert O2.remaining_quantity == 5
    assert market.order_infos[O2.order_id].remaining_qty == 5

    assert len(market.cancelled_orders) == 1
    assert O2.order_id in market.cancelled_orders

    assert engine.event_queue.empty()

    """
    Expected Events

    t = 0: Run Strategy

    t = 2: Order 1 Arrives at Market (Order 1 is completed)
    t = 2: Order 2 Arrives at Market

    t = 4: Fill 1 arrives at Broker
    t = 4: Fill 2 arrives at Broker

    t = 5: Run Strategy

    t = 7: Cancellation Arrives at Market

    t = 7: Update Market (Order 2 should not get filled)

    t = 9: Cancellation arrives at Broker

    """