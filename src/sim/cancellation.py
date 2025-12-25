from dataclasses import dataclass
from enum import Enum
from typing import Dict,List,TYPE_CHECKING

import pandas as pd

from sim.cancellation_submission import CancellationSubmission

if TYPE_CHECKING:
    from sim import *

class CancellationState(Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"
    NO_OP = "NO_OP"

class CancellationSnapshot:
    def __init__(self, cancellation : "Cancellation") -> None:
        self.state = cancellation.state
        self.order_id = cancellation.order_id
        self.submission_ts = cancellation.submission_ts

class Cancellation:
    state : "CancellationState"
    order_id : int
    submission_ts : pd.Timestamp

    def __init__(self,order_id, submission_ts) -> None:
        self.order_id = order_id
        self.submission_ts = submission_ts
        self.state = CancellationState.CREATED

    def _to_submit(self):
        if self.state == CancellationState.CREATED:
            self.state = CancellationState.SUBMITTED
            return True
        return False
    
    def _to_cancelled(self):
        if self.state == CancellationState.SUBMITTED:
            self.state = CancellationState.CANCELLED
            return True
        return False
    
    def _to_no_op(self):
        if self.state == CancellationState.SUBMITTED:
            self.state = CancellationState.NO_OP
            return True
        return False
    
    def get_submission(self) -> "CancellationSubmission":
        return CancellationSubmission(self.order_id)
    
    def get_snapshot(self):
        return CancellationSnapshot(self)