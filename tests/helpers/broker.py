import pandas as pd

from sim import *

def get_simple_broker_delta():
    delta = pd.Timedelta(days=1)
    return Broker(0,PerShareFee(0),delta),delta

def create_live_order(broker,order_req,ts):
    ev = broker.handle_requests(ts, [order_req], [])[0]
    order_id = ev.order_submission.order_id
    broker.orders[order_id]._to_live()
    return order_id