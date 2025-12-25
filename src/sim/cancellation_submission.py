from dataclasses import dataclass

@dataclass(frozen=True)
class CancellationSubmission:
    order_id : int