from dataclasses import dataclass
from typing import TYPE_CHECKING,Dict

from sim.order_request import OrderSide

if TYPE_CHECKING:
    from sim import *

@dataclass(frozen=True)
class PortfolioSnapshot:
    cash : float
    positions : Dict[str,int]
    average_costs : Dict[str,float]
    realized_pnl : float

class Portfolio:
    cash : float
    positions : Dict[str,int]
    average_costs : Dict[str,float]
    realized_pnl : float

    def __init__(self, cash : float) -> None:
        self.cash = cash

        self.positions = {}
        self.average_costs = {}
        self.realized_pnl = 0
        

    def add_fill(self, fill : "Fill"):
        trade_value = fill.qty * fill.fill_price

        symbol = fill.symbol
        if not symbol in self.positions:
            self.positions[symbol] = 0
            self.average_costs[symbol] = 0
        
        position = self.positions[symbol]
        avg_cost = self.average_costs[symbol]

        if fill.side == OrderSide.BUY:
            if self.cash < trade_value:
                raise RuntimeError("Portfolio attempted to buy more than current cash.")

            self.average_costs[symbol] = (avg_cost * position + trade_value) / (position + fill.qty)

            self.cash -= trade_value
            self.positions[symbol] += fill.qty

        elif fill.side == OrderSide.SELL:
            if self.positions[symbol] < fill.qty:
                raise RuntimeError("Portfolio attempted to sell more than current position.")

            self.realized_pnl += (fill.fill_price - avg_cost) * fill.qty

            self.cash +=trade_value
            self.positions[symbol] -= fill.qty

            if self.positions[symbol] == 0:
                self.average_costs[symbol] = 0
            
    def apply_fee(self, fee : float):
        if fee < 0:
            raise ValueError(f"Portfolio attempted to use negative fee. ({fee})")
        if self.cash < fee:
            raise RuntimeError("Portfolio can not afford fee.")
        self.cash -= fee
    
    def get_position(self, symbol : str):
        return self.positions.get(symbol,0)

    def get_snapshot(self):
        return PortfolioSnapshot(
            cash=self.cash,
            positions=self.positions,
            average_costs=self.average_costs,
            realized_pnl=self.realized_pnl
        )