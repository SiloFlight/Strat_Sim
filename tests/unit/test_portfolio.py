import pytest

from sim import *
import helpers

def test_add_fill():
    P1 = Portfolio(100)

    buy_fill = Fill(0,10,OrderSide.BUY,10,helpers.misc.get_simple_ts())
    sell_fill = Fill(0,10,OrderSide.SELL,10,helpers.misc.get_simple_ts())

    P1.add_fill(buy_fill)

    assert P1.cash == 0
    assert P1.position == 10
    assert P1.average_cost == 10

    P1.add_fill(sell_fill)

    assert P1.cash == 100
    assert P1.position == 0
    assert P1.average_cost == 0

    with pytest.raises(RuntimeError,match="more than current cash"):
        temp_port = Portfolio(0)

        temp_port.add_fill(buy_fill)
    
    with pytest.raises(RuntimeError,match="more than current position"):
        temp_port = Portfolio(100)

        temp_port.add_fill(sell_fill)


    P2 = Portfolio(100)

    buy1 = Fill(0,5,OrderSide.BUY,10,helpers.misc.get_simple_ts())
    buy2 = Fill(0,10,OrderSide.BUY,5,helpers.misc.get_simple_ts())

    P2.add_fill(buy1)
    P2.add_fill(buy2)

    assert P2.cash == 0
    assert P2.average_cost ==  pytest.approx(100 / 15)
    
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