# src/book.py
from dataclasses import dataclass
from typing import List, Dict, Optional


# Representa uma ordem no livro
@dataclass
class Order:
    order_type: str
    side: str
    qty: int
    price: Optional[float] = None
    ts: int = 0
    id: Optional[str] = None
    pegged: Optional[str] = None


# Armazena o estado e operações do livro de ordens
class OrderBook:
    # Inicializa o livro de ordens
    def __init__(self):
        self.buys: List[Order] = []
        self.sells: List[Order] = []
        self._ts_counter = 0
        self._id_counter = 0
        self.orders_by_id: Dict[str, Order] = {}

    # Gera o próximo timestamp lógico global
    def _next_ts(self) -> int:
        self._ts_counter += 1
        return self._ts_counter

    # Gera o próximo identificador de ordem
    def _next_id(self) -> str:
        self._id_counter += 1
        return f"identificador_{self._id_counter}"

    # Retorna o melhor preço de compra não pegged
    def best_bid(self) -> Optional[float]:
        best = None
        for o in self.buys:
            if o.pegged == "bid" or o.price is None:
                continue
            if best is None or o.price > best:
                best = o.price
        return best

    # Retorna o melhor preço de venda não pegged
    def best_offer(self) -> Optional[float]:
        best = None
        for o in self.sells:
            if o.pegged == "offer" or o.price is None:
                continue
            if best is None or o.price < best:
                best = o.price
        return best

    # Imprime o livro de ordens em formato tabular
    def print_book(self):
        buy_rows = [f"{o.qty} @ {o.price}" for o in self.buys]
        sell_rows = [f"{o.qty} @ {o.price}" for o in self.sells]

        rows = max(len(buy_rows), len(sell_rows), 1)
        buy_rows += [""] * (rows - len(buy_rows))
        sell_rows += [""] * (rows - len(sell_rows))

        buy_header = "Ordens de Compra"
        sell_header = "Ordens de Venda"

        col1_width = len(buy_header)
        for r in buy_rows:
            if len(r) > col1_width:
                col1_width = len(r)
        col1_width += 2

        col2_width = len(sell_header)
        for r in sell_rows:
            if len(r) > col2_width:
                col2_width = len(r)
        col2_width += 2

        sep = "+" + "-" * col1_width + "+" + "-" * col2_width + "+"

        print(sep)
        print(
            "| "
            + buy_header.ljust(col1_width - 2)
            + " | "
            + sell_header.ljust(col2_width - 2)
            + " | "
        )
        print(sep)
        for b, s in zip(buy_rows, sell_rows):
            print(
                "| "
                + b.ljust(col1_width - 2)
                + " | "
                + s.ljust(col2_width - 2)
                + " | "
            )
        print(sep)

    # Processa a entrada de uma ordem limit
    def handle_limit(self, side: str, price: float, qty: int):
        import limit, pegged

        ts = self._next_ts()
        if side == "buy":
            limit.match_limit_buy(self, price, qty, ts)
        else:
            limit.match_limit_sell(self, price, qty, ts)
        pegged.update_pegged_to_bid(self)
        pegged.update_pegged_to_offer(self)

    # Cancela uma ordem existente por identificador
    def cancel_order(self, order_id: str):
        import limit, pegged

        limit.cancel_order(self, order_id)
        pegged.update_pegged_to_bid(self)
        pegged.update_pegged_to_offer(self)

    # Modifica apenas a quantidade de uma ordem pegged
    def modify_order_qty_only(self, order_id: str, new_qty: int):
        import limit

        limit.modify_order_qty_only(self, order_id, new_qty)

    # Modifica preço e quantidade de uma ordem limit existente
    def modify_order(self, order_id: str, new_price: float, new_qty: int):
        import limit, pegged

        limit.modify_order(self, order_id, new_price, new_qty)
        pegged.update_pegged_to_bid(self)
        pegged.update_pegged_to_offer(self)

    # Processa a entrada de uma ordem market
    def handle_market(self, side: str, qty: int):
        import market, pegged

        ts = self._next_ts()
        if side == "buy":
            market.match_market_buy(self, qty, ts)
        else:
            market.match_market_sell(self, qty, ts)
        pegged.update_pegged_to_bid(self)
        pegged.update_pegged_to_offer(self)

    # Processa a entrada de uma ordem pegged
    def handle_peg(self, reference: str, side: str, qty: int):
        import pegged

        ts = self._next_ts()
        pegged.handle_peg(self, reference, side, qty, ts)