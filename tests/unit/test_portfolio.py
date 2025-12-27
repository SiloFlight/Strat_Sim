import pytest

from sim import *
import helpers

def test_add_fill():
    P1 = Portfolio(100)
    symbol = "sym1"

    buy_fill = Fill(order_id=0,qty=10,symbol=symbol,side=OrderSide.BUY,fill_price=10,ts=helpers.misc.get_simple_ts())
    sell_fill = Fill(order_id=0,qty=10,symbol=symbol,side=OrderSide.SELL,fill_price=10,ts=helpers.misc.get_simple_ts())
    P1.add_fill(buy_fill)

    assert P1.cash == 0
    assert P1.positions[symbol] == 10
    assert P1.average_costs[symbol] == 10

    P1.add_fill(sell_fill)

    assert P1.cash == 100
    assert P1.positions[symbol] == 0
    assert P1.average_costs[symbol] == 0

    with pytest.raises(RuntimeError,match="more than current cash"):
        temp_port = Portfolio(0)

        temp_port.add_fill(buy_fill)
    
    with pytest.raises(RuntimeError,match="more than current position"):
        temp_port = Portfolio(100)

        temp_port.add_fill(sell_fill)


    P2 = Portfolio(100)

    buy1 = Fill(order_id=0,qty=5,symbol=symbol,side=OrderSide.BUY,fill_price=10,ts=helpers.misc.get_simple_ts())
    buy2 = Fill(order_id=0,qty=10,symbol=symbol,side=OrderSide.BUY,fill_price=5,ts=helpers.misc.get_simple_ts())

    P2.add_fill(buy1)
    P2.add_fill(buy2)

    assert P2.cash == 0
    assert P2.average_costs[symbol] ==  pytest.approx(100 / 15)
    
def test_apply_fee():
    P1 = Portfolio(100)

    P1.apply_fee(100)
    
    assert P1.cash == 0

    with pytest.raises(ValueError,match="negative fee"):
        P1.apply_fee(-1)

        assert P1.cash == 0
    
    with pytest.raises(RuntimeError,match="can not afford fee"):
        P1.apply_fee(1)

        assert P1.cash == 0

def test_symbol_isolation():
    P1 = Portfolio(100)
    S1,S2 = "sym1","sym2"

    buy_fill = Fill(order_id=0,qty=10,symbol=S1,side=OrderSide.BUY,fill_price=10,ts=helpers.misc.get_simple_ts())

    P1.add_fill(buy_fill)

    assert P1.get_position(S1) == 10
    assert P1.get_position(S2) == 0