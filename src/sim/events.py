from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from sim import *

class EventType(Enum):
    RUN_STRATEGY = "RUN_STRATEGY"
    UPDATE_MARKET_DATA =  "UPDATE_MARKET_DATA"
    ORDER_ARRIVES_AT_MARKET = "ORDER_ARRIVES_AT_MARKET"
    CANCELLATION_ARRIVES_AT_MARKET = "CANCELLATION_ARRIVES_AT_MARKET"
    FILL_ARRIVES_AT_BROKER = "FILL_ARRIVES_AT_BROKER"
    CANCELLATION_ARRIVES_AT_BROKER = "CANCELLATION_ARRIVES_AT_BROKER"

@dataclass(frozen=True)
class Event:
    event_type : EventType
    ts : pd.Timestamp

@dataclass(frozen=True)
class RunStrategyEvent(Event):
    pass

@dataclass(frozen=True)
class UpdateMarketDataEvent(Event):
    pass

@dataclass(frozen=True)
class OrderArrivesAtMarketEvent(Event):
    order_submission : "OrderSubmission"

@dataclass(frozen=True)
class CancellationArrivesAtMarketEvent(Event):
    cancellation_submission : "CancellationSubmission"

@dataclass(frozen=True)
class FillArrivesAtBrokerEvent(Event):
    fill : "Fill"

@dataclass(frozen=True)
class CancellationArrivesAtBrokerEvent(Event):
    cancellation_result : "CancellationResult"