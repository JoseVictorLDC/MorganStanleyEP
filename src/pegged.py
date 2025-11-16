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
        to_delete = []
        for oid, order in list(book.orders_by_id.items()):
            if order.side == "buy" and order.pegged == "bid":
                for i, o in enumerate(book.buys):
                    if o is order:
                        book.buys.pop(i)
                        break
                to_delete.append(oid)
                print(f"Pegged order cancelled (no bid reference) {oid}")
        for oid in to_delete:
            book.orders_by_id.pop(oid, None)
        return

    for order in list(book.orders_by_id.values()):
        if order.side == "buy" and order.pegged == "bid":
            if order.price == best:
                continue

            for i, o in enumerate(book.buys):
                if o is order:
                    book.buys.pop(i)
                    break

            order.price = best
            order.ts = book._next_ts()
            limit.add_buy_limit(book, order)

# Atualiza ordens pegged ligadas ao melhor offer
def update_pegged_to_offer(book):
    best = book.best_offer()
    if best is None:
        to_delete = []
        for oid, order in list(book.orders_by_id.items()):
            if order.side == "sell" and order.pegged == "offer":
                for i, o in enumerate(book.sells):
                    if o is order:
                        book.sells.pop(i)
                        break
                to_delete.append(oid)
                print(f"Pegged order cancelled (no offer reference) {oid}")
        for oid in to_delete:
            book.orders_by_id.pop(oid, None)
        return

    for order in list(book.orders_by_id.values()):
        if order.side == "sell" and order.pegged == "offer":
            if order.price == best:
                continue

            for i, o in enumerate(book.sells):
                if o is order:
                    book.sells.pop(i)
                    break

            order.price = best
            order.ts = book._next_ts()
            limit.add_sell_limit(book, order)