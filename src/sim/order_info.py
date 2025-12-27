from dataclasses import dataclass
from typing import Optional,TYPE_CHECKING

import pandas as pd

from sim.order_request import OrderType

if TYPE_CHECKING:
    from sim import *

@dataclass
class OrderInfo():
    order_id : int
    arrival_time : pd.Timestamp
    side : "OrderSide"
    remaining_qty : int
    order_type : "OrderType"
    symbol : str
    limit : Optional[float] = None

    def reduce_quantity(self, qty : int):
        if qty <= 0:
            raise ValueError(f"reduce_quantity attempted with non positive qty ({qty}).")
        if qty > self.remaining_qty:
            raise ValueError(f"reduce_quantity attempted with more than remaining qty ({qty})")
        self.remaining_qty -= qty

    def __post_init__(self):
        #Validate Qty
        if self.remaining_qty <= 0:
            raise ValueError(f"OrderInfo created with non-positive quantity ({self.remaining_qty}).")

        #Validate limit exists if limit order or stop_limit
        if self.order_type == OrderType.LIMIT and not self.limit:
            raise ValueError("OrderInfo created with limit type, but limit was not provided.")
        
        #Validate limit
        if self.limit and self.limit <= 0:
            raise ValueError(f"OrderInfo created with non-positive limit ({self.limit}).")