from abc import ABC,abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sim import *

class FillLogic(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def calculate_fill_qty(self, order_info : "OrderInfo") -> int:
        pass

class CappedFill(FillLogic):
    max_fill : int
    
    def __init__(self, max_fill : int) -> None:
        super().__init__()

        self.max_fill = max_fill
    
    def calculate_fill_qty(self, order_info: "OrderInfo") -> int:
        return min(self.max_fill,order_info.remaining_qty)