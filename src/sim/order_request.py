from dataclasses import dataclass
from enum import Enum
from typing import Optional

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

@dataclass(frozen=True)
class OrderRequest():
    side : OrderSide
    order_type : OrderType
    qty : int
    symbol : str
    limit : Optional[float] = None


    def __post_init__(self):
        #Validate Qty
        if self.qty <= 0:
            raise ValueError(f"OrderRequest created with non-positive quantity ({self.qty}).")

        #Validate limit exists if limit order or stop_limit
        if self.order_type == OrderType.LIMIT and not self.limit:
            raise ValueError("OrderRequest created with limit type, but limit was not provided.")
        
        #Validate limit
        if self.limit and self.limit <= 0:
            raise ValueError(f"OrderRequested created with non-positive limit ({self.limit}).")