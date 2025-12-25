from abc import ABC,abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sim import *

class FeeModel(ABC):
    @abstractmethod
    def calculate_fee(self,fill : "Fill") -> float:
        pass

class PerShareFee(FeeModel):
    def __init__(self, share_fee : float) -> None:
        self.share_fee = share_fee
    
    def calculate_fee(self, fill: "Fill") -> float:
        return self.share_fee * fill.qty