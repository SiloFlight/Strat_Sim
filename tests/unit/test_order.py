from dataclasses import dataclass

import pandas as pd
import pytest

from sim import *

from helpers.order import *

@dataclass
class ExpectedTransitions:
    submitted : bool
    live : bool
    filled : bool
    partially_filled : bool
    cancel_pending : bool
    cancelled : bool

def assert_expected_state_transitions(order_func, expected_transitions : ExpectedTransitions):
    original_state = order_func().state

    transitions = [
        ("_to_submitted",expected_transitions.submitted,OrderState.SUBMITTED),
        ("_to_live",expected_transitions.live,OrderState.LIVE),
        ("_to_filled",expected_transitions.filled,OrderState.FILLED),
        ("_to_partially_filled",expected_transitions.partially_filled,OrderState.PARTIALLY_FILLED),
        ("_to_cancel_pending",expected_transitions.cancel_pending,OrderState.CANCEL_PENDING),
        ("_to_cancelled",expected_transitions.cancelled,OrderState.CANCELLED),
    ]

    for transition_name, expected_op_status, result_state in transitions:
        order = order_func()

        transition_fn = getattr(order,transition_name)
        assert transition_fn() == expected_op_status

        assert order.state == result_state if expected_op_status else original_state

def test_created_transitions():
    assert get_created_order().state == OrderState.CREATED

    transitions = ExpectedTransitions(submitted=True,live=False,filled=False,partially_filled=False,cancel_pending=False,cancelled=False)

    assert_expected_state_transitions(get_created_order,transitions)

def test_submitted_transitions():
    assert get_submitted_order().state == OrderState.SUBMITTED

    transitions = ExpectedTransitions(submitted=False,live=True,filled=False,partially_filled=False,cancel_pending=False,cancelled=False)

    assert_expected_state_transitions(get_submitted_order,transitions)

def test_live_transitions():
    assert get_live_order().state == OrderState.LIVE

    transitions = ExpectedTransitions(submitted=False,live=False,filled=True,partially_filled=True,cancel_pending=True,cancelled=False)

    assert_expected_state_transitions(get_live_order,transitions)

def test_partially_filled_transitions():
    assert get_partially_filled_order().state == OrderState.PARTIALLY_FILLED

    transitions = ExpectedTransitions(submitted=False,live=False,filled=True,partially_filled=False,cancel_pending=True,cancelled=False)

    assert_expected_state_transitions(get_partially_filled_order,transitions)

def test_filled_transitions():
    assert get_filled_order().state == OrderState.FILLED

    transitions = ExpectedTransitions(submitted=False,live=False,filled=False,partially_filled=False,cancel_pending=False,cancelled=False)

    assert_expected_state_transitions(get_filled_order,transitions)

def test_cancel_pending_transitions():
    assert get_cancel_pending_order().state == OrderState.CANCEL_PENDING

    transitions = ExpectedTransitions(submitted=False,live=False,filled=True,partially_filled=False,cancel_pending=False,cancelled=True)

    assert_expected_state_transitions(get_cancel_pending_order,transitions)

def test_cancelled_transitions():
    assert get_cancelled_order().state == OrderState.CANCELLED

    transitions = ExpectedTransitions(submitted=False,live=False,filled=False,partially_filled=False,cancel_pending=False,cancelled=False)

    assert_expected_state_transitions(get_cancelled_order,transitions)

def test_add_fill():
    # Live -> Partial Fill -> Filled
    O1 = get_live_order()
    init_qty = O1.qty
    symbol = "sym1"
    f1 = Fill(order_id=0,qty=init_qty//2,symbol=symbol,side=OrderSide.BUY,fill_price=10,ts=pd.Timestamp("2000-01-01"))
    f2 = Fill(order_id=0,qty=init_qty-init_qty//2,symbol=symbol,side=OrderSide.BUY,fill_price=10,ts=pd.Timestamp("2000-01-01"))

    O1.add_fill(f1)

    assert O1.remaining_quantity == init_qty - init_qty//2
    assert O1.state == OrderState.PARTIALLY_FILLED

    O1.add_fill(f2)

    assert O1.remaining_quantity == 0
    assert O1.state == OrderState.FILLED

    # Live -> Filled
    O2 = get_live_order()
    fill = Fill(order_id=0,qty=init_qty,symbol=symbol,side=OrderSide.BUY,fill_price=10,ts=pd.Timestamp("2000-01-01"))

    O2.add_fill(fill)

    assert O2.remaining_quantity == 0
    assert O2.state == OrderState.FILLED

    # Larger Fill than Possible
    with pytest.raises(ValueError,match="greater than remaining qty"):
        get_live_order().add_fill(Fill(order_id=0,qty=init_qty+1,symbol=symbol,side=OrderSide.BUY,fill_price=10,ts=pd.Timestamp("2000-01-01")))
    
    with pytest.raises(RuntimeError,match="invalid order state"):
        get_created_order().add_fill(fill)

    with pytest.raises(RuntimeError,match="invalid order state"):
        get_submitted_order().add_fill(fill)
        
    with pytest.raises(RuntimeError,match="invalid order state"):
        get_cancelled_order().add_fill(fill)
    
    with pytest.raises(RuntimeError,match="invalid order state"):
        get_filled_order().add_fill(fill)