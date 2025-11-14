from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Order:
    order_type: str   # "limit" ou "market"
    side: str         # "buy" ou "sell"
    qty: int
    price: Optional[float] = None  # só para limit
    ts: int = 0                    # timestamp lógico (para FIFO)


class OrderBook:
    def __init__(self):
        self.buys: List[Order] = []   # ordens de compra
        self.sells: List[Order] = []  # ordens de venda
        self._ts_counter = 0          # gerador de timestamp

    # ------------- utilidades básicas -------------

    def _next_ts(self) -> int:
        self._ts_counter += 1
        return self._ts_counter

    def _add_buy_limit(self, order: Order):
        """
        Insere em self.buys ordenado por:
        - maior preço primeiro
        - em empate de preço, menor ts (mais antigo) primeiro
        """
        i = 0
        while i < len(self.buys):
            o = self.buys[i]
            if order.price > o.price:
                break
            if order.price == o.price and order.ts < o.ts:
                break
            i += 1
        self.buys.insert(i, order)

    def _add_sell_limit(self, order: Order):
        """
        Insere em self.sells ordenado por:
        - menor preço primeiro
        - em empate de preço, menor ts (mais antigo) primeiro
        """
        i = 0
        while i < len(self.sells):
            o = self.sells[i]
            if order.price < o.price:
                break
            if order.price == o.price and order.ts < o.ts:
                break
            i += 1
        self.sells.insert(i, order)

    # ------------- entrada de ordens públicas -------------

    def handle_limit(self, side: str, price: float, qty: int):
        ts = self._next_ts()
        if side == "buy":
            self._match_limit_buy(price, qty, ts)
        else:
            self._match_limit_sell(price, qty, ts)

    def handle_market(self, side: str, qty: int):
        ts = self._next_ts()
        if side == "buy":
            self._match_market_buy(qty, ts)
        else:
            self._match_market_sell(qty, ts)

    def print_book(self):
        # monta as linhas como strings
        buy_rows = [f"{o.qty} @ {o.price}" for o in self.buys]
        sell_rows = [f"{o.qty} @ {o.price}" for o in self.sells]

        # garante que as duas listas tenham o mesmo tamanho
        rows = max(len(buy_rows), len(sell_rows))
        buy_rows += [""] * (rows - len(buy_rows))
        sell_rows += [""] * (rows - len(sell_rows))

        # cabeçalhos
        buy_header = "Ordens de Compra"
        sell_header = "Ordens de Venda"

        # largura das colunas
        col1_width = max(len(buy_header), *(len(r) for r in buy_rows)) + 2
        col2_width = max(len(sell_header), *(len(r) for r in sell_rows)) + 2

        # separador
        sep = "+" + "-" * col1_width + "+" + "-" * col2_width + "+"

        # imprime tabela
        print(sep)
        print(
            "| "
            + buy_header.ljust(col1_width - 2)
            + " | "
            + sell_header.ljust(col2_width - 2)
            + " |"
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


    # ------------- lógica de matching: LIMIT -------------

    def _match_limit_buy(self, price: float, qty: int, ts: int):
        """
        Limit buy:
        - Casa contra melhores vendas enquanto sell.price <= price
        - Sobra entra como ordem passiva de compra
        """
        trades = {}  # price -> total_qty
        while qty > 0 and self.sells and self.sells[0].price <= price:
            best = self.sells[0]
            trade_qty = min(qty, best.qty)
            trade_price = best.price

            trades[trade_price] = trades.get(trade_price, 0) + trade_qty

            qty -= trade_qty
            best.qty -= trade_qty

            if best.qty == 0:
                self.sells.pop(0)

        # imprime os trades dessa ordem
        for p, q in trades.items():
            print(f"Trade, price: {p}, qty: {q}")

        # se sobrou quantidade, vira buy limit passiva
        if qty > 0:
            new_order = Order(
                order_type="limit",
                side="buy",
                qty=qty,
                price=price,
                ts=ts,
            )
            self._add_buy_limit(new_order)

    def _match_limit_sell(self, price: float, qty: int, ts: int):
        """
        Limit sell:
        - Casa contra melhores compras enquanto buy.price >= price
        - Sobra entra como ordem passiva de venda
        """
        trades = {}  # price -> total_qty
        while qty > 0 and self.buys and self.buys[0].price >= price:
            best = self.buys[0]
            trade_qty = min(qty, best.qty)
            trade_price = best.price

            trades[trade_price] = trades.get(trade_price, 0) + trade_qty

            qty -= trade_qty
            best.qty -= trade_qty

            if best.qty == 0:
                self.buys.pop(0)

        for p, q in trades.items():
            print(f"Trade, price: {p}, qty: {q}")

        if qty > 0:
            new_order = Order(
                order_type="limit",
                side="sell",
                qty=qty,
                price=price,
                ts=ts,
            )
            self._add_sell_limit(new_order)

    # ------------- lógica de matching: MARKET -------------

    def _match_market_buy(self, qty: int, ts: int):
        """
        Market buy:
        - Casa contra melhores vendas até acabar qty ou o book
        - Se sobrar qty e tiver havido trade, o resto vira LIMIT BUY
          no último preço de trade (com mesmo ts da ordem original).
        """
        trades = {}
        last_trade_price = None

        while qty > 0 and self.sells:
            best = self.sells[0]
            trade_qty = min(qty, best.qty)
            trade_price = best.price

            trades[trade_price] = trades.get(trade_price, 0) + trade_qty
            last_trade_price = trade_price

            qty -= trade_qty
            best.qty -= trade_qty

            if best.qty == 0:
                self.sells.pop(0)

        for p, q in trades.items():
            print(f"Trade, price: {p}, qty: {q}")

    def _match_market_sell(self, qty: int, ts: int):
        """
        Market sell:
        - Casa contra melhores compras até acabar qty ou o book
        - Se sobrar qty e tiver havido trade, o resto vira LIMIT SELL
          no último preço de trade (com mesmo ts da ordem original).
        """
        trades = {}
        last_trade_price = None

        while qty > 0 and self.buys:
            best = self.buys[0]
            trade_qty = min(qty, best.qty)
            trade_price = best.price

            trades[trade_price] = trades.get(trade_price, 0) + trade_qty
            last_trade_price = trade_price

            qty -= trade_qty
            best.qty -= trade_qty

            if best.qty == 0:
                self.buys.pop(0)

        for p, q in trades.items():
            print(f"Trade, price: {p}, qty: {q}")

# --------- loop de terminal ---------

def process_line(book: OrderBook, line: str):
    parts = line.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()

    if cmd in ("exit", "quit"):
        raise SystemExit

    if cmd == "print" and len(parts) >= 2 and parts[1] == "book":
        book.print_book()
        return

    if cmd == "limit":
        # limit buy 10 100
        if len(parts) != 4:
            print("Uso: limit <buy/sell> <price> <qty>")
            return
        _, side, price, qty = parts
        side = side.lower()
        price = float(price)
        qty = int(qty)
        book.handle_limit(side, price, qty)
        return

    if cmd == "market":
        # market buy 150
        if len(parts) != 3:
            print("Uso: market <buy/sell> <qty>")
            return
        _, side, qty = parts
        side = side.lower()
        qty = int(qty)
        book.handle_market(side, qty)
        return

    print("Comando desconhecido. Exemplos:")
    print("  limit buy 10 100")
    print("  market sell 50")
    print("  print book")
    print("  exit")


if __name__ == "__main__":
    book = OrderBook()
    print("Matching Engine simples. Comandos:")
    print("  limit buy 10 100")
    print("  market sell 50")
    print("  print book")
    print("  exit")
    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break
        try:
            process_line(book, line)
        except SystemExit:
            break