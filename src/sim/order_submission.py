from dataclasses import dataclass
from typing import Optional,TYPE_CHECKING

import pandas as pd

from sim.order_info import OrderInfo,OrderType

if TYPE_CHECKING:
    from sim import *

@dataclass(frozen=True)
class OrderSubmission():
    order_id : int
    side : "OrderSide"
    qty : int
    symbol : str
    order_type : "OrderType"
    limit : Optional[float] = None

    def __post_init__(self):
        #Validate Qty
        if self.qty <= 0:
            raise ValueError(f"OrderSubmission created with non-positive quantity ({self.qty}).")

        #Validate limit exists if limit order or stop_limit
        if self.order_type == OrderType.LIMIT and not self.limit:
            raise ValueError("OrderSubmission created with limit type, but limit was not provided.")
        
        #Validate limit
        if self.limit and self.limit <= 0:
            raise ValueError(f"OrderSubmission created with non-positive limit ({self.limit}).")
        
    def get_info(self, arrival_time : pd.Timestamp):
        return OrderInfo(order_id=self.order_id,
                         arrival_time=arrival_time,
                         side=self.side,
                         remaining_qty=self.qty,
                         order_type=self.order_type,
                         limit=self.limit,
                         symbol=self.symbol)