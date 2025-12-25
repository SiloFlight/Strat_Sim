from typing import Dict,List,TYPE_CHECKING

import pandas as pd

from sim.order import Order
from sim.portfolio import Portfolio,PortfolioSnapshot
from sim.events import Event,EventType,OrderArrivesAtMarketEvent,CancellationArrivesAtMarketEvent
from sim.cancellation import Cancellation
from sim.cancellation_result import CancellationOutcome

if TYPE_CHECKING:
    from sim import *

"""
Broker

Responsibilities
- Coordinate communication of requests from strategy to the market.
- Own portfolio representation.
- Own order state info for strategy observation.

Design Note - V1: The broker currently has very few guardrails on request execution. The broker only catches references to invalid order_ids. Invalid execution states from fills are captured by as fatal errors by Portfolio.
"""

class BrokerSnapshot:
    def __init__(self, broker : "Broker") -> None:
        self.portfolio = broker.portfolio.get_snapshot()
        self.cancellations = {order_id : cancellation.get_snapshot() for order_id, cancellation in broker.cancellations.items()}
        self.orders = {order_id : order.get_snapshot() for order_id, order in broker.orders.items()}

class Broker:
    fee_model : "FeeModel"
    latency : pd.Timedelta
    orders : Dict[int,"Order"]
    cancellations : Dict[int,"Cancellation"]
    portfolio : "Portfolio"

    current_order_id : int

    def __init__(self, initial_cash : float, fee_model : "FeeModel", latency : pd.Timedelta) -> None:
        self.fee_model = fee_model
        self.latency = latency

        self.orders = {}
        self.cancellations = {}
        self.portfolio = Portfolio(initial_cash)
        self.current_order_id = 0

    def handle_requests(self, ts : pd.Timestamp ,order_requests : List["OrderRequest"], cancellation_requests : List["CancellationRequest"]) -> List["Event"]:
        events = []

        for order_req in order_requests:
            new_order = Order(order_req,self._generate_order_id())
            order_id = new_order.order_id
            self.orders[order_id] = new_order

            new_order._to_submitted()

            submission = new_order.get_submission()
            
            events.append(OrderArrivesAtMarketEvent(EventType.ORDER_ARRIVES_AT_MARKET,ts+self.latency,submission))

        for cancel_req in cancellation_requests:
            if not cancel_req.order_id in self.orders:
                raise RuntimeError("Cancellation Request for non existent order.")

            new_cancellation = Cancellation(cancel_req.order_id,ts)
            self.cancellations[cancel_req.order_id] = new_cancellation

            new_cancellation._to_submit()
            self.orders[cancel_req.order_id]._to_cancel_pending()

            submission = new_cancellation.get_submission()

            events.append(CancellationArrivesAtMarketEvent(EventType.CANCELLATION_ARRIVES_AT_MARKET,ts+self.latency,submission))

        return events
    
    def handle_order_arrival(self, order_id : int) -> None:
        if not order_id in self.orders:
            raise RuntimeError("Attempted arrival of nonexistent order.")
        
        self.orders[order_id]._to_live()

    def handle_fill(self, fill : "Fill") -> None:
        order_id = fill.order_id
        if not order_id in self.orders:
            raise RuntimeError("Attempted fill on nonexistent order.")
        
        if not fill.side == self.orders[order_id].side:
            raise RuntimeError("Order and Fill side disagree.")
        
        self.orders[order_id].add_fill(fill)
        self.portfolio.add_fill(fill)
        self.portfolio.apply_fee(self.fee_model.calculate_fee(fill))

    def handle_cancellation_result(self, result : "CancellationResult") -> None:
        order_id = result.order_id

        if not order_id in self.orders:
            raise RuntimeError("Broker received CancellationResult for nonexistent order.")

        if not order_id in self.cancellations:
            raise RuntimeError("Broker received CancellationResult for non cancelled order.")

        if result.cancellation_outcome == CancellationOutcome.CANCELLED:
            self.cancellations[order_id]._to_cancelled()
            self.orders[order_id]._to_cancelled()
        elif result.cancellation_outcome == CancellationOutcome.NO_OP:
            self.cancellations[order_id]._to_no_op()

    def _generate_order_id(self) -> int:
        order_id = self.current_order_id
        self.current_order_id += 1
        
        return order_id
    
    def get_snapshot(self):
        return BrokerSnapshot(self)