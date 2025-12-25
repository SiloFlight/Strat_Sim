from abc import ABC,abstractmethod
from typing import List,Tuple,TYPE_CHECKING

if TYPE_CHECKING:
    from sim import *

class Strategy(ABC):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> Tuple[List["OrderRequest"],List["CancellationRequest"]]:
        return [],[]