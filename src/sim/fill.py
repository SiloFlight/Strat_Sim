from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from sim import *

@dataclass(frozen=True)
class Fill:
    order_id : int
    qty : int
    symbol : str
    side : "OrderSide"
    fill_price : float
    ts : pd.Timestamp

    def __post_init__(self):
        if self.qty <= 0:
            raise ValueError(f"Fill created with nonpositive qty ({self.qty}).")