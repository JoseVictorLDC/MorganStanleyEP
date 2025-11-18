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
    i = 0
    sells = book.sells
    while qty > 0 and i < len(sells) and sells[i].price <= price:
        best = sells[i]
        trade_qty = min(qty, best.qty)
        trade_price = best.price
        print(f"Trade, price: {trade_price}, qty: {trade_qty}")

        qty -= trade_qty
        best.qty -= trade_qty
        if best.qty == 0:
            i += 1
        else:
            break
    if i > 0:
        book.sells = sells[i:]
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
    i = 0
    buys = book.buys
    while qty > 0 and i < len(buys) and buys[i].price >= price:
        best = buys[i]
        trade_qty = min(qty, best.qty)
        trade_price = best.price
        print(f"Trade, price: {trade_price}, qty: {trade_qty}")

        qty -= trade_qty
        best.qty -= trade_qty
        if best.qty == 0:
            i += 1
        else:
            break
    if i > 0:
        book.buys = buys[i:]
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

# Altera preço e quantidade de uma ordem limit existente
def modify_order(book, order_id: str, new_price: float, new_qty: int):
    order = book.orders_by_id.get(order_id)
    if order is None:
        print("Order not found")
        return
    if order.pegged is not None:
        print("Ordem é pegged. Use: modify order <id> <qty> para alterar ordens pegged.")
        return
    old_price = order.price
    old_qty = order.qty
    side = order.side
    if new_qty <= 0:
        book_list = book.buys if side == "buy" else book.sells
        for i, o in enumerate(book_list):
            if o is order:
                book_list.pop(i)
                break
        book.orders_by_id.pop(order_id, None)
        print("Order cancelled by qty change")
        return
    if new_price == old_price:
        if new_qty <= old_qty:
            order.qty = new_qty
            print(f"Order modified: {side} {new_qty} @ {new_price} {order_id}")
            return
        else:
            book_list = book.buys if side == "buy" else book.sells
            for i, o in enumerate(book_list):
                if o is order:
                    book_list.pop(i)
                    break

            order.qty = new_qty
            order.ts = book._next_ts()

            if side == "buy":
                add_buy_limit(book, order)
            else:
                add_sell_limit(book, order)

            print(f"Order modified: {side} {new_qty} @ {new_price} {order_id}")
            return

    book_list = book.buys if side == "buy" else book.sells
    for i, o in enumerate(book_list):
        if o is order:
            book_list.pop(i)
            break
    ts = book._next_ts()
    if side == "buy":
        match_limit_buy(book, new_price, new_qty, ts, existing_order=order)
    else:
        match_limit_sell(book, new_price, new_qty, ts, existing_order=order)