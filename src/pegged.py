# src/pegged.py
from book import Order
import limit

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
    print(f"Pegged order created: buy {qty} @ {best} (peg to bid) {order_id}")

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
    print(f"Pegged order created: sell {qty} @ {best} (peg to offer) {order_id}")

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

    higher = []
    equal_normal = []
    pegged = []
    lower = []
    for o in book.buys:
        if o.pegged == "bid":
            o.price = best
            o.ts = book._next_ts()
            pegged.append(o)
        else:
            p = o.price
            if p is None:
                lower.append(o)
            elif p > best:
                higher.append(o)
            elif p == best:
                equal_normal.append(o)
            else:
                lower.append(o)

    book.buys = higher + equal_normal + pegged + lower

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

    below = []
    equal_normal = []
    pegged = []
    above = []
    for o in book.sells:
        if o.pegged == "offer":
            o.price = best
            o.ts = book._next_ts()
            pegged.append(o)
        else:
            p = o.price
            if p is None:
                above.append(o)
            elif p < best:
                below.append(o)
            elif p == best:
                equal_normal.append(o)
            else:
                above.append(o)

    book.sells = below + equal_normal + pegged + above