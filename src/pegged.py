# src/pegged.py
from book import Order
import limit

# Funções auxiliares de ordenação de buy
def _buy_sort_key(o: Order):
    p = o.price if o.price is not None else float("-inf")
    return (-p, o.ts)

# Funções auxiliares de ordenação de sell
def _sell_sort_key(o: Order):
    p = o.price if o.price is not None else float("inf")
    return (p, o.ts) 

# Processa o comando peg e delega a criação da ordem
def handle_peg(book, reference: str, side: str, qty: int, ts: int):
    reference = reference.lower()
    side = side.lower()
    if reference == "bid" and side == "buy":
        create_pegged_bid_buy(book, qty, ts)
    elif reference == "offer" and side == "sell":
        create_pegged_offer_sell(book, qty, ts)
    else:
        print("Combinação de peg inválida. Use: peg bid buy <qty> ou peg offer sell <qty>")

# Cria uma ordem pegged de compra atrelada ao melhor bid
def create_pegged_bid_buy(book, qty: int, ts: int):
    best = book.best_bid()
    if best is None:
        print("Não há bid para fazer peg.")
        return
    order_id = book._next_id()
    order = Order(
        order_type="limit",
        side="buy",
        qty=qty,
        price=best,
        ts=ts,
        id=order_id,
        pegged="bid",
    )
    limit.add_buy_limit(book, order)
    book.orders_by_id[order_id] = order
    print(f"Order created: buy {qty} @ {best} {order_id}")

# Cria uma ordem pegged de venda atrelada ao melhor offer
def create_pegged_offer_sell(book, qty: int, ts: int):
    best = book.best_offer()
    if best is None:
        print("Não há offer para fazer peg.")
        return
    order_id = book._next_id()
    order = Order(
        order_type="limit",
        side="sell",
        qty=qty,
        price=best,
        ts=ts,
        id=order_id,
        pegged="offer",
    )
    limit.add_sell_limit(book, order)
    book.orders_by_id[order_id] = order
    print(f"Order created: sell {qty} @ {best} {order_id}")

# Atualiza ordens pegged ligadas ao melhor bid
def update_pegged_to_bid(book):
    best = book.best_bid()
    if best is None:
        new_buys = []
        for o in book.buys:
            if o.pegged == "bid":
                if o.id is not None:
                    book.orders_by_id.pop(o.id, None)
                print(f"Pegged order cancelled (no bid reference) {o.id}")
            else:
                new_buys.append(o)
        book.buys = new_buys
        return

    for o in book.buys:
        if o.pegged == "bid":
            o.price = best
    book.buys.sort(key=_buy_sort_key)

# Atualiza ordens pegged ligadas ao melhor offer
def update_pegged_to_offer(book):
    best = book.best_offer()
    if best is None:
        new_sells = []
        for o in book.sells:
            if o.pegged == "offer":
                if o.id is not None:
                    book.orders_by_id.pop(o.id, None)
                print(f"Pegged order cancelled (no offer reference) {o.id}")
            else:
                new_sells.append(o)
        book.sells = new_sells
        return

    for o in book.sells:
        if o.pegged == "offer":
            o.price = best
    book.sells.sort(key=_sell_sort_key)

# Altera apenas a quantidade de uma ordem pegged
def modify_pegged_qty(book, order_id: str, new_qty: int):
    order = book.orders_by_id.get(order_id)
    if order is None:
        print("Order not found")
        return
    if order.pegged is None:
        print("Ordem não é pegged. Use: modify order <id> <price> <qty> para ordens limit.")
        return
    old_qty = order.qty
    if new_qty <= 0:
        book_list = book.buys if order.side == "buy" else book.sells
        for i, o in enumerate(book_list):
            if o is order:
                book_list.pop(i)
                break
        book.orders_by_id.pop(order_id, None)
        print(f"Pegged order cancelled by qty change {order_id}")
        return
    if new_qty <= old_qty:
        order.qty = new_qty
        print(f"Order modified: {order.side} {new_qty} @ {order.price} {order_id}")
        return
    book_list = book.buys if order.side == "buy" else book.sells
    for i, o in enumerate(book_list):
        if o is order:
            book_list.pop(i)
            break

    order.qty = new_qty
    order.ts = book._next_ts()
    if order.side == "buy":
        limit.add_buy_limit(book, order)
    else:
        limit.add_sell_limit(book, order)
    print(f"Order modified: {order.side} {new_qty} @ {order.price} {order_id}")