from dataclasses import dataclass
from enum import Enum

import pandas as pd

class CancellationOutcome(Enum):
    NO_OP = "NO_OP"
    CANCELLED = "CANCELLED"

@dataclass(frozen=True)
class CancellationResult:
    order_id : int
    ts : pd.Timestamp
    cancellation_outcome : CancellationOutcome