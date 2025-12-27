from sim import *

def get_created_order():
    return Order(
        OrderRequest(side=OrderSide.BUY,order_type=OrderType.MARKET,qty=100,symbol=""),0)

def get_submitted_order():
    order = get_created_order()
    order._to_submitted()

    return order

def get_live_order():
    order = get_submitted_order()
    order._to_live()

    return order

def get_partially_filled_order():
    order = get_live_order()
    order._to_partially_filled()

    return order

def get_filled_order():
    order = get_live_order()
    order._to_filled()

    return order

def get_cancel_pending_order():
    order = get_live_order()
    order._to_cancel_pending()

    return order

def get_cancelled_order():
    order = get_cancel_pending_order()
    order._to_cancelled()

    return order