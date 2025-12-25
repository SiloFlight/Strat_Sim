from dataclasses import dataclass
from typing import TYPE_CHECKING

from sim.order_request import OrderSide

if TYPE_CHECKING:
    from sim import *

@dataclass(frozen=True)
class PortfolioSnapshot:
    cash : float
    position : int
    average_cost : float
    realized_pnl : float

class Portfolio:
    cash : float
    position : int = 0
    average_cost : float = 0
    realized_pnl : float = 0

    def __init__(self, cash : float) -> None:
        self.cash = cash

    def add_fill(self, fill : "Fill"):
        trade_value = fill.qty * fill.fill_price

        if fill.side == OrderSide.BUY:
            if self.cash < trade_value:
                raise RuntimeError("Portfolio attempted to buy more than current cash.")

            self.average_cost = (self.average_cost * self.position + trade_value) / (self.position + fill.qty)

            self.cash -= trade_value
            self.position += fill.qty

        elif fill.side == OrderSide.SELL:
            if self.position < fill.qty:
                raise RuntimeError("Portfolio attempted to sell more than current position.")

            self.realized_pnl += (fill.fill_price - self.average_cost) * fill.qty

            self.cash +=trade_value
            self.position -= fill.qty

            if self.position == 0:
                self.average_cost = 0
            
    def apply_fee(self, fee : float):
        if fee < 0:
            raise ValueError(f"Portfolio attempted to use negative fee. ({fee})")
        if self.cash < fee:
            raise RuntimeError("Portfolio can not afford fee.")
        self.cash -= fee

    def get_snapshot(self):
        return PortfolioSnapshot(
            cash=self.cash,
            position=self.position,
            average_cost=self.average_cost,
            realized_pnl=self.realized_pnl
        )