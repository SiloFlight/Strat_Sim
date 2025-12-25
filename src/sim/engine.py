from typing import Dict,Type,TypeVar,Tuple,TYPE_CHECKING
from queue import PriorityQueue

import pandas as pd

from sim.events import Event,EventType,RunStrategyEvent,UpdateMarketDataEvent,FillArrivesAtBrokerEvent,OrderArrivesAtMarketEvent,CancellationArrivesAtBrokerEvent,CancellationArrivesAtMarketEvent

if TYPE_CHECKING:
    from sim import *

EVENT_PRIORITIES : Dict[EventType,int] = {
    EventType.CANCELLATION_ARRIVES_AT_MARKET : 0,
    EventType.UPDATE_MARKET_DATA : 1,
    EventType.ORDER_ARRIVES_AT_MARKET : 2,
    EventType.CANCELLATION_ARRIVES_AT_BROKER : 3,
    EventType.FILL_ARRIVES_AT_BROKER : 4,
    EventType.RUN_STRATEGY : 5
}


T = TypeVar("T",bound=Event)
def safe_event_cast(event : Event, cls: Type[T]) -> T:
    if not isinstance(event,cls):
        raise TypeError("Invalid event cast")

    return event

"""
Engine

Responsibilities
- Controls strate mutation. Component state mutation only occurs when engine validates.
- Coordinate intra object communication
- Control event queue and execution order
- Guarantee execution queue respects temporal and priority restrictions

Design Notes - V1: Engine is extremely minimal in its guardrails. All errors that are not queue related are caught downstream.
"""

class Engine:
    strategy : "Strategy"
    broker : "Broker"
    market : "Market"
    ts : pd.Timestamp

    event_queue : PriorityQueue[Tuple[pd.Timestamp,int,int,"Event"]]
    enqueue_id : int

    def __init__(self, strategy : "Strategy", broker : "Broker",market : "Market") -> None:
        self.strategy = strategy
        self.broker = broker
        self.market = market

        self.event_queue = PriorityQueue()
        self.enqueue_id = 0
        self.ts = pd.Timestamp(0)
    
    def insert_event(self, event : "Event") -> bool:
        ts = event.ts
        if ts < self.ts:
            raise RuntimeError("Attempt to enqueue past event.")
        
        self.event_queue.put((ts,EVENT_PRIORITIES[event.event_type],self.get_enqueue_id(),event))

        return True
    
    def process_event(self, event : "Event") -> None:
        ts = event.ts
        if ts < self.ts:
            raise RuntimeError("Past event within queue.")
        self.ts = ts
        
        match event.event_type:
            case EventType.CANCELLATION_ARRIVES_AT_MARKET:
                event = safe_event_cast(event,CancellationArrivesAtMarketEvent)
                
                results = self.market.handle_cancellation_arrival(ts,event.cancellation_submission)

                for ev in results:
                    self.insert_event(ev)

            case EventType.UPDATE_MARKET_DATA:
                event = safe_event_cast(event,UpdateMarketDataEvent)

                results = self.market.handle_market_update(ts)

                for ev in results:
                    self.insert_event(ev)
                
            case EventType.ORDER_ARRIVES_AT_MARKET:
                event = safe_event_cast(event,OrderArrivesAtMarketEvent)

                results = self.market.handle_order_arrival(ts,event.order_submission)
                self.broker.handle_order_arrival(event.order_submission.order_id)

                for ev in results:
                    self.insert_event(ev)

            case EventType.CANCELLATION_ARRIVES_AT_BROKER:
                event = safe_event_cast(event,CancellationArrivesAtBrokerEvent)

                self.broker.handle_cancellation_result(event.cancellation_result)

            case EventType.FILL_ARRIVES_AT_BROKER:
                event = safe_event_cast(event,FillArrivesAtBrokerEvent)

                self.broker.handle_fill(event.fill)
            case EventType.RUN_STRATEGY:
                event = safe_event_cast(event,RunStrategyEvent)

                results = self.strategy.run()

                for ev in self.broker.handle_requests(ts,*results):
                    self.insert_event(ev)
    
    def run(self) -> None:
        while not self.event_queue.empty():
            ts,priority,enqueue_id,event = self.event_queue.get()

            self.process_event(event)

    
    def get_enqueue_id(self) -> int:
        enqueue_id = self.enqueue_id
        self.enqueue_id += 1
        return enqueue_id