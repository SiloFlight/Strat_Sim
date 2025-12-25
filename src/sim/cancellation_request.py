from dataclasses import dataclass

@dataclass(frozen=True)
class CancellationRequest:
    order_id : int