from enum import Enum
from typing import List,Optional,TYPE_CHECKING
from dataclasses import dataclass

from sim.order_submission import OrderSubmission

if TYPE_CHECKING:
    from sim import *

"Needed Imports: OrderSubmission"

class OrderState(Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    LIVE = "LIVE"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY"
    CANCEL_PENDING = "CANCEL_PENDING"
    CANCELLED = "CANCELLED"

class OrderSnapshot():
   def __init__(self, order : "Order") -> None:
       self.order_id = order.order_id
       self.side = order.side
       self.order_type = order.order_type
       self.qty = order.qty
       self.state = order.state
       self.fills = order.fills
       self.limit = order.limit
   
class Order():
    order_id : int
    side : "OrderSide"
    order_type : "OrderType"
    qty : int
    state : "OrderState"
    fills : List["Fill"]
    limit : Optional[float] = None

    def __init__(self, order_request : "OrderRequest", order_id : int) -> None:
        self.order_id = order_id
        self.side  = order_request.side
        self.order_type = order_request.order_type
        self.qty = order_request.qty
        self.limit = order_request.limit

        self.state = OrderState.CREATED
        self.fills = []
    
    def add_fill(self,fill : "Fill"):
        if self.state not in [OrderState.LIVE,OrderState.PARTIALLY_FILLED,OrderState.CANCEL_PENDING]:
            raise RuntimeError(f"add_fill attempted in invalid order state ({self.state})")
        
        if fill.qty > self.remaining_quantity:
            raise ValueError(f"add_fill attempted with greater than remaining qty. ({self.qty})")

        self.fills.append(fill)

        if self.remaining_quantity == 0:
            self._to_filled()
        else:
            self._to_partially_filled()

    
    def _to_submitted(self) -> bool:
        if self.state == OrderState.CREATED:
            self.state = OrderState.SUBMITTED
            return True
        return False
    
    def _to_live(self) -> bool:
        if self.state in [OrderState.SUBMITTED]:
            self.state = OrderState.LIVE
            return True
        return False
    
    def _to_partially_filled(self) -> bool:
        if self.state in [OrderState.LIVE]:
            self.state = OrderState.PARTIALLY_FILLED
            return True
        return False
    
    def _to_cancel_pending(self) -> bool:
        if self.state in [OrderState.LIVE,OrderState.PARTIALLY_FILLED]:
            self.state = OrderState.CANCEL_PENDING
            return True
        return False
    
    def _to_cancelled(self) -> bool:
        if self.state in [OrderState.CANCEL_PENDING]:
            self.state = OrderState.CANCELLED
            return True
        return False
    
    def _to_filled(self) -> bool:
        if self.state in [OrderState.LIVE,OrderState.PARTIALLY_FILLED,OrderState.CANCEL_PENDING]:
            self.state = OrderState.FILLED
            return True
        return False
    
    def get_submission(self):
        return OrderSubmission(self.order_id,self.side,self.qty,self.order_type,self.limit)
    

    @property
    def remaining_quantity(self) -> int:
        fill_quantities = [fill.qty for fill in self.fills]

        return self.qty - sum(fill_quantities)
    
    @property
    def average_fill_price(self) -> Optional[float]:
        fill_prices = [fill.qty * fill.fill_price for fill in self.fills]
        fill_qty = self.qty - self.remaining_quantity

        if fill_qty == 0:
            return None
        else:
            return sum(fill_prices) / fill_qty
    
    def get_snapshot(self):
        return OrderSnapshot(self)