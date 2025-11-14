from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Order:
    order_type: str   # "limit" ou "market"
    side: str         # "buy" ou "sell"
    qty: int
    price: Optional[float] = None  # só para limit
    ts: int = 0                    # timestamp lógico (para FIFO)
    id: Optional[str] = None       # identificador
    pegged: Optional[str] = None   # None, "bid" ou "offer"

class OrderBook:
    def __init__(self):
        self.buys: List[Order] = []   # ordens de compra
        self.sells: List[Order] = []  # ordens de venda
        self._ts_counter = 0          # gerador de timestamp
        self.orders_by_id: dict[str, Order] = {}  # id -> Order (somente LIMIT ativas)

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

    def best_bid(self) -> Optional[float]:
        return self.buys[0].price if self.buys else None

    def best_offer(self) -> Optional[float]:
        return self.sells[0].price if self.sells else None

    # ------------- entrada de ordens públicas -------------

    def handle_limit(self, side: str, price: float, qty: int):
        ts = self._next_ts()
        if side == "buy":
            self._match_limit_buy(price, qty, ts)
        else:
            self._match_limit_sell(price, qty, ts)

        # livro pode ter mudado → atualiza peggeds
        self._update_pegged_to_bid()
        self._update_pegged_to_offer()

    def handle_market(self, side: str, qty: int):
        ts = self._next_ts()
        if side == "buy":
            self._match_market_buy(qty, ts)
        else:
            self._match_market_sell(qty, ts)

        self._update_pegged_to_bid()
        self._update_pegged_to_offer()

    def handle_peg(self, reference: str, side: str, qty: int):
        ts = self._next_ts()
        reference = reference.lower()
        side = side.lower()

        if reference == "bid" and side == "buy":
            self._create_pegged_bid_buy(qty, ts)
        elif reference == "offer" and side == "sell":
            self._create_pegged_offer_sell(qty, ts)
        else:
            print("Combinação de peg inválida. Use: peg bid buy <qty> ou peg offer sell <qty>")

    def print_book(self):
        # monta as linhas como strings
        buy_rows = [f"{o.qty} @ {o.price}" for o in self.buys]
        sell_rows = [f"{o.qty} @ {o.price}" for o in self.sells]

        # pelo menos 1 linha para a tabela não sumir quando estiver vazia
        rows = max(len(buy_rows), len(sell_rows), 1)
        buy_rows += [""] * (rows - len(buy_rows))
        sell_rows += [""] * (rows - len(sell_rows))

        # cabeçalhos
        buy_header = "Ordens de Compra"
        sell_header = "Ordens de Venda"

        # largura das colunas (sem usar splat, para não quebrar quando lista está vazia)
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

        # separador
        sep = "+" + "-" * col1_width + "+" + "-" * col2_width + "+"

        # imprime tabela
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

    # ------------- lógica de matching: LIMIT -------------

    def _match_limit_buy(self, price: float, qty: int, ts: int, existing_id: Optional[str] = None):
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
            order_id = existing_id or f"identificador_{ts}"
            new_order = Order(
                order_type="limit",
                side="buy",
                qty=qty,
                price=price,
                ts=ts,
                id=order_id,
            )
            self._add_buy_limit(new_order)
            self.orders_by_id[order_id] = new_order
            if existing_id:
                print(f"Order modified: buy {qty} @ {price} {order_id}")
            else:
                print(f"Order created: buy {qty} @ {price} {order_id}")

    def _match_limit_sell(self, price: float, qty: int, ts: int, existing_id: Optional[str] = None):
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
            order_id = existing_id or f"identificador_{ts}"
            new_order = Order(
                order_type="limit",
                side="sell",
                qty=qty,
                price=price,
                ts=ts,
                id=order_id,
            )
            self._add_sell_limit(new_order)
            self.orders_by_id[order_id] = new_order
            if existing_id:
                print(f"Order modified: sell {qty} @ {price} {order_id}")
            else:
                print(f"Order created: sell {qty} @ {price} {order_id}")

    def cancel_order(self, order_id: str):
        """
        Cancela uma LIMIT order ainda ativa no book.
        """
        order = self.orders_by_id.pop(order_id, None)
        if order is None:
            print("Order not found")
            return

        book_list = self.buys if order.side == "buy" else self.sells

        for i, o in enumerate(book_list):
            if o is order:
                book_list.pop(i)
                print("Order cancelled")
                return

        # se chegou aqui, a ordem já não estava mais no book (foi totalmente executada)
        print("Order already filled or not active")

        self._update_pegged_to_bid()
        self._update_pegged_to_offer()

    def modify_order(self, order_id: str, new_price: float, new_qty: int):
        """
        Modifica uma LIMIT order ativa:
        - remove do book,
        - executa como se fosse uma nova limit (pode gerar trades),
        - se sobrar qty, entra de novo no book com mesmo id mas novo ts
          (perde prioridade).
        """
        order = self.orders_by_id.pop(order_id, None)
        if order is None:
            print("Order not found")
            return

        # remove a ordem antiga da lista (buy ou sell)
        book_list = self.buys if order.side == "buy" else self.sells
        for i, o in enumerate(book_list):
            if o is order:
                book_list.pop(i)
                break

        # novo timestamp => perde prioridade
        ts = self._next_ts()
        side = order.side

        # re-insere passando o mesmo id, usando o matching normal
        if side == "buy":
            self._match_limit_buy(new_price, new_qty, ts, existing_id=order_id)
        else:
            self._match_limit_sell(new_price, new_qty, ts, existing_id=order_id)

        self._update_pegged_to_bid()
        self._update_pegged_to_offer()

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

    def _create_pegged_bid_buy(self, qty: int, ts: int):
        best = self.best_bid()
        if best is None:
            print("Não há bid para fazer peg.")
            return

        order_id = f"order_{ts}"
        order = Order(
            order_type="limit",
            side="buy",
            qty=qty,
            price=best,
            ts=ts,
            id=order_id,
            pegged="bid",
        )
        self._add_buy_limit(order)
        self.orders_by_id[order_id] = order
        print(f"Pegged order created: buy {qty} @ {best} (peg to bid) {order_id}")

    def _create_pegged_offer_sell(self, qty: int, ts: int):
        best = self.best_offer()
        if best is None:
            print("Não há offer para fazer peg.")
            return

        order_id = f"order_{ts}"
        order = Order(
            order_type="limit",
            side="sell",
            qty=qty,
            price=best,
            ts=ts,
            id=order_id,
            pegged="offer",
        )
        self._add_sell_limit(order)
        self.orders_by_id[order_id] = order
        print(f"Pegged order created: sell {qty} @ {best} (peg to offer) {order_id}")
    
    def _update_pegged_to_bid(self):
        best = self.best_bid()
        if best is None:
            return

        # percorre só ordens pegged ao bid
        for order in list(self.orders_by_id.values()):
            if order.side == "buy" and order.pegged == "bid":
                if order.price == best:
                    continue  # já está no preço certo

                # remove da lista de buys
                for i, o in enumerate(self.buys):
                    if o is order:
                        self.buys.pop(i)
                        break

                # atualiza preço e reinsere mantendo o ts (prioridade antiga)
                order.price = best
                self._add_buy_limit(order)

    def _update_pegged_to_offer(self):
        best = self.best_offer()
        if best is None:
            return

        for order in list(self.orders_by_id.values()):
            if order.side == "sell" and order.pegged == "offer":
                if order.price == best:
                    continue

                for i, o in enumerate(self.sells):
                    if o is order:
                        self.sells.pop(i)
                        break

                order.price = best
                self._add_sell_limit(order)

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
    
    if cmd == "cancel":
        # cancel order order_1
        if len(parts) != 3 or parts[1].lower() != "order":
            print("Uso: cancel order <id>")
            return
        order_id = parts[2]
        book.cancel_order(order_id)
        return

    if cmd == "modify":
        # modify order order_1 9.98 200
        if len(parts) != 5 or parts[1].lower() != "order":
            print("Uso: modify order <id> <price> <qty>")
            return
        _, _, order_id, price, qty = parts
        price = float(price)
        qty = int(qty)
        book.modify_order(order_id, price, qty)
        return
    
    if cmd == "peg":
        # peg bid buy 150
        if len(parts) != 4:
            print("Uso: peg <bid/offer> <buy/sell> <qty>")
            return
        _, reference, side, qty = parts
        qty = int(qty)
        book.handle_peg(reference, side, qty)
        return


    print("Comando desconhecido. Exemplos:")
    print("  limit buy 10 100")
    print("  market sell 50")
    print("  print book")
    print("  exit")


if __name__ == "__main__":
    book = OrderBook()
    print("Matching Engine simples. Comandos:")
    print("  tipo side price(ponto como separador) qty")
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