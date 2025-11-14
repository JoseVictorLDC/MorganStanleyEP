# src/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Order:
    order_type: str          # "limit" ou "market"
    side: str                # "buy" ou "sell"
    qty: int
    price: Optional[float] = None  # só para limit
    ts: int = 0                     # timestamp lógico (para FIFO)
    id: Optional[str] = None        # identificador
    pegged: Optional[str] = None    # None, "bid" ou "offer"