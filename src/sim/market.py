from typing import List,Set,Dict,Optional,TYPE_CHECKING

import pandas as pd

from sim import CancellationResult,FillArrivesAtBrokerEvent,CancellationArrivesAtBrokerEvent,Fill,EventType,CancellationOutcome,OrderType,OrderSide

if TYPE_CHECKING:
    from sim import *

"""
Market

Responsibilities:
- Own execution logic and fill communication.

Design Notes - V1: Currently a single symbol structure. Will be extended to allow multiple symbols.
"""

class MarketSnapshot:
    market_datas : Dict[str,"MarketDataSnapshot"]
    def __init__(self, market : "Market", ts : pd.Timestamp) -> None:
        self.market_datas = {symbol : market_data.get_snapshot(ts) for symbol, market_data in market.market_datas.items()}
    
    def get_symbols(self) -> List[str]:
        return list(self.market_datas.keys())

class Market:
    market_datas : Dict[str,"MarketData"]
    order_infos : Dict[int,"OrderInfo"]
    cancelled_orders : Set[int]
    current_ts : pd.Timestamp
    fill_logic : "FillLogic"
    latency : pd.Timedelta

    def __init__(self, market_datas : Dict[str,"MarketData"], fill_logic : "FillLogic", latency : pd.Timedelta) -> None:
        self.market_datas = market_datas
        self.latency = latency
        self.fill_logic = fill_logic

        self.cancelled_orders = set()
        self.order_infos = {}
    
    def _calculate_fill_qty(self, order_info : "OrderInfo") -> int:
        fill_qty = self.fill_logic.calculate_fill_qty(order_info)

        if fill_qty < 0:
            raise RuntimeError("FillLogic generated negative fill_qty.")
        
        return fill_qty

    def _calculate_fill_price(self, symbol : str, ts : pd.Timestamp) -> Optional[float]:
        fill_bar = self.market_datas[symbol].current_bar(ts)

        if fill_bar == None:
            return None
        
        return fill_bar.open


    def calculate_fill(self, order_info : "OrderInfo", ts : pd.Timestamp) -> Optional["Fill"]:
        fill_qty = self._calculate_fill_qty(order_info)
        fill_price = self._calculate_fill_price(order_info.symbol,ts)
        
        if fill_price == None or fill_qty == 0:
            return None
        
        fill = Fill(order_id=order_info.order_id,
                    qty=fill_qty,
                    symbol=order_info.symbol,
                    side=order_info.side,
                    fill_price=fill_price,
                    ts=ts)

        return fill
    
    def is_price_executable(self, order_info : "OrderInfo", fill : Fill) -> bool:
        if order_info.order_type == OrderType.MARKET:
            return True
        
        if order_info.order_type == OrderType.LIMIT:
            if order_info.limit == None:
                raise RuntimeError("Limit order lacking limit.")
            
            if order_info.side == OrderSide.BUY:
                return fill.fill_price <= order_info.limit
            
            if order_info.side == OrderSide.SELL:
                return fill.fill_price >= order_info.limit
        
        raise RuntimeError(f"Unknown Order Type:{order_info.order_type}")
    
    def process_order_info(self, order_info : "OrderInfo", ts : pd.Timestamp) -> List["Event"]:
        order_id, arrival_time = order_info.order_id, order_info.arrival_time
        if arrival_time > ts:
            raise RuntimeError("Order processed before arrival time.")
        
        if order_id in self.cancelled_orders:
            return []
        
        fill = self.calculate_fill(order_info,ts)

        if fill == None:
            return []
        
        if not self.is_price_executable(order_info, fill):
            return []
        
        self.order_infos[order_id].reduce_quantity(fill.qty)
        
        return [FillArrivesAtBrokerEvent(EventType.FILL_ARRIVES_AT_BROKER,ts + self.latency,fill)]

    
    def handle_market_update(self, ts : pd.Timestamp) -> List["Event"]:
        events = []

        for order_info in self.order_infos.values():
            events += self.process_order_info(order_info,ts)

        return events
    
    def handle_order_arrival(self, ts : pd.Timestamp, order_submission : "OrderSubmission") -> List["Event"]:
        order_info = order_submission.get_info(ts)
        order_id = order_info.order_id
        self.order_infos[order_id] = order_info

        return self.process_order_info(order_info,ts)
    
    def handle_cancellation_arrival(self, ts : pd.Timestamp, cancellation_submission : "CancellationSubmission") -> List["Event"]:
        order_id = cancellation_submission.order_id

        self.cancelled_orders.add(order_id)

        if order_id not in self.order_infos or self.order_infos[order_id].remaining_qty > 0:
            cancellation_result = CancellationResult(order_id,ts,CancellationOutcome.CANCELLED)
            return [CancellationArrivesAtBrokerEvent(EventType.CANCELLATION_ARRIVES_AT_BROKER,ts+self.latency,cancellation_result)]
        
        cancellation_result = CancellationResult(order_id,ts,CancellationOutcome.NO_OP)
        return [CancellationArrivesAtBrokerEvent(EventType.CANCELLATION_ARRIVES_AT_BROKER,ts+self.latency,cancellation_result)]
    
    def get_snapshot(self, ts : pd.Timestamp):
        return MarketSnapshot(self,ts)
