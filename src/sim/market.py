from typing import List,Set,Dict,Optional,TYPE_CHECKING

import pandas as pd

from sim import CancellationResult,FillArrivesAtBrokerEvent,CancellationArrivesAtBrokerEvent,Fill,EventType,CancellationOutcome

if TYPE_CHECKING:
    from sim import *

"""
Market

Responsibilities:
- Own execution logic and fill communication.

Design Notes - V1: Currently a single symbol structure. Will be extended to allow multiple symbols.
"""

class Market:
    market_data : "MarketData"
    order_infos : Dict[int,"OrderInfo"]
    cancelled_orders : Set[int]
    current_ts : pd.Timestamp
    fill_logic : "FillLogic"
    latency : pd.Timedelta

    def __init__(self, market_data : "MarketData", fill_logic : "FillLogic", latency : pd.Timedelta) -> None:
        self.market_data = market_data
        self.latency = latency
        self.fill_logic = fill_logic

        self.cancelled_orders = set()
        self.order_infos = {}
    
    def calculate_fill(self, order_info : "OrderInfo", ts : pd.Timestamp) -> Optional["Fill"]:
        fill_qty = self.fill_logic.calculate_fill_qty(order_info)
        fill_bar = self.market_data.current_bar(ts)

        if fill_bar == None or fill_qty == 0:
                return None
        
        fill = Fill(order_info.order_id,fill_qty,order_info.side,fill_bar.open,ts)

        return fill

    
    def handle_market_update(self, ts : pd.Timestamp) -> List["Event"]:
        events = []

        for order_id, order_info in self.order_infos.items():
            arrival_time = order_info.arrival_time

            if arrival_time >= ts or order_id in self.cancelled_orders:
                continue

            fill = self.calculate_fill(order_info,ts)

            if fill == None:
                continue

            self.order_infos[order_id].reduce_quantity(fill.qty)

            events.append(FillArrivesAtBrokerEvent(EventType.FILL_ARRIVES_AT_BROKER,ts + self.latency,fill))

        return events
    
    def handle_order_arrival(self, ts : pd.Timestamp, order_submission : "OrderSubmission") -> List["Event"]:
        order_info = order_submission.get_info(ts)
        order_id = order_info.order_id
        self.order_infos[order_id] = order_info

        if order_id in self.cancelled_orders:
            return []
        
        fill = self.calculate_fill(order_info,ts)

        if fill == None:
            return []
        
        self.order_infos[order_id].reduce_quantity(fill.qty)

        return[FillArrivesAtBrokerEvent(EventType.FILL_ARRIVES_AT_BROKER,ts + self.latency,fill)]
    
    def handle_cancellation_arrival(self, ts : pd.Timestamp, cancellation_submission : "CancellationSubmission") -> List["Event"]:
        order_id = cancellation_submission.order_id

        self.cancelled_orders.add(order_id)

        if order_id not in self.order_infos or self.order_infos[order_id].remaining_qty > 0:
            cancellation_result = CancellationResult(order_id,ts,CancellationOutcome.CANCELLED)
            return [CancellationArrivesAtBrokerEvent(EventType.CANCELLATION_ARRIVES_AT_BROKER,ts+self.latency,cancellation_result)]
        
        cancellation_result = CancellationResult(order_id,ts,CancellationOutcome.NO_OP)
        return [CancellationArrivesAtBrokerEvent(EventType.CANCELLATION_ARRIVES_AT_BROKER,ts+self.latency,cancellation_result)]
