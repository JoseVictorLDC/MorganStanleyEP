# src/limit.py
from typing import Optional
from book import Order

# Insere ordem de compra na lista mantendo ordenação
def add_buy_limit(book, order: Order):
    i = 0
    while i < len(book.buys):
        o = book.buys[i]

        if order.price > o.price:
            break
        if order.price < o.price:
            i += 1
            continue

        if order.ts < o.ts:
            break

        i += 1

    book.buys.insert(i, order)

# Insere ordem de venda na lista mantendo ordenação
def add_sell_limit(book, order: Order):
    i = 0
    while i < len(book.sells):
        o = book.sells[i]

        if order.price < o.price:
            break
        if order.price > o.price:
            i += 1
            continue

        if order.ts < o.ts:
            break

        i += 1

    book.sells.insert(i, order)

# Processa uma ordem limit de compra
def match_limit_buy(book, price: float, qty: int, ts: int, existing_order: Optional[Order] = None):
    trades = {}
    while qty > 0 and book.sells and book.sells[0].price <= price:
        best = book.sells[0]
        trade_qty = min(qty, best.qty)
        trade_price = best.price

        trades[trade_price] = trades.get(trade_price, 0) + trade_qty

        qty -= trade_qty
        best.qty -= trade_qty

        if best.qty == 0:
            book.sells.pop(0)

    for p, q in trades.items():
        print(f"Trade, price: {p}, qty: {q}")

    if qty > 0:
        if existing_order is None:
            order_id = book._next_id()
            new_order = Order(
                order_type="limit",
                side="buy",
                qty=qty,
                price=price,
                ts=ts,
                id=order_id,
            )
            add_buy_limit(book, new_order)
            book.orders_by_id[order_id] = new_order
            print(f"Order created: buy {qty} @ {price} {order_id}")
        else:
            existing_order.price = price
            existing_order.qty = qty
            existing_order.ts = ts
            add_buy_limit(book, existing_order)
            print(f"Order modified: buy {qty} @ {price} {existing_order.id}")
    else:
        if existing_order is not None:
            book.orders_by_id.pop(existing_order.id, None)
            print(f"Order fully filled: buy {price} {existing_order.id}")

# Processa uma ordem limit de venda
def match_limit_sell(book, price: float, qty: int, ts: int, existing_order: Optional[Order] = None):
    trades = {}
    while qty > 0 and book.buys and book.buys[0].price >= price:
        best = book.buys[0]
        trade_qty = min(qty, best.qty)
        trade_price = best.price

        trades[trade_price] = trades.get(trade_price, 0) + trade_qty

        qty -= trade_qty
        best.qty -= trade_qty

        if best.qty == 0:
            book.buys.pop(0)

    for p, q in trades.items():
        print(f"Trade, price: {p}, qty: {q}")

    if qty > 0:
        if existing_order is None:
            order_id = book._next_id()
            new_order = Order(
                order_type="limit",
                side="sell",
                qty=qty,
                price=price,
                ts=ts,
                id=order_id,
            )
            add_sell_limit(book, new_order)
            book.orders_by_id[order_id] = new_order
            print(f"Order created: sell {qty} @ {price} {order_id}")
        else:
            existing_order.price = price
            existing_order.qty = qty
            existing_order.ts = ts
            add_sell_limit(book, existing_order)
            print(f"Order modified: sell {qty} @ {price} {existing_order.id}")
    else:
        if existing_order is not None:
            book.orders_by_id.pop(existing_order.id, None)
            print(f"Order fully filled: sell {price} {existing_order.id}")

# Cancela uma ordem limit ativa
def cancel_order(book, order_id: str):
    order = book.orders_by_id.pop(order_id, None)
    if order is None:
        print("Order not found")
        return

    book_list = book.buys if order.side == "buy" else book.sells

    for i, o in enumerate(book_list):
        if o is order:
            book_list.pop(i)
            print("Order cancelled")
            break
    else:
        print("Order already filled or not active")

# Altera apenas a quantidade de uma ordem pegged
def modify_order_qty_only(book, order_id: str, new_qty: int):
    order = book.orders_by_id.get(order_id)
    if order is None:
        print("Order not found")
        return

    if order.pegged is None:
        print("Para ordens limit normais use: modify order <id> <price> <qty>")
        return

    order.qty = new_qty
    print(f"Pegged order modified: {order.side} {new_qty} @ {order.price} {order_id}")

# Altera preço e quantidade de uma ordem limit existente
def modify_order(book, order_id: str, new_price: float, new_qty: int):
    order = book.orders_by_id.get(order_id)
    if order is None:
        print("Order not found")
        return

    if order.pegged is not None:
        order.qty = new_qty
        print(f"Pegged order modified: {order.side} {new_qty} @ {order.price} {order_id}")
        return

    book_list = book.buys if order.side == "buy" else book.sells
    for i, o in enumerate(book_list):
        if o is order:
            book_list.pop(i)
            break

    ts = book._next_ts()
    side = order.side

    if side == "buy":
        match_limit_buy(book, new_price, new_qty, ts, existing_order=order)
    else:
        match_limit_sell(book, new_price, new_qty, ts, existing_order=order)