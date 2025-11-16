# src/market.py
# Processa uma ordem market de compra
def match_market_buy(book, qty: int, ts: int):
    trades = {}
    last_trade_price = None

    while qty > 0 and book.sells:
        best = book.sells[0]
        trade_qty = min(qty, best.qty)
        trade_price = best.price

        trades[trade_price] = trades.get(trade_price, 0) + trade_qty
        last_trade_price = trade_price

        qty -= trade_qty
        best.qty -= trade_qty

        if best.qty == 0:
            book.sells.pop(0)

    for p, q in trades.items():
        print(f"Trade, price: {p}, qty: {q}")

# Processa uma ordem market de venda
def match_market_sell(book, qty: int, ts: int):
    trades = {}
    last_trade_price = None

    while qty > 0 and book.buys:
        best = book.buys[0]
        trade_qty = min(qty, best.qty)
        trade_price = best.price

        trades[trade_price] = trades.get(trade_price, 0) + trade_qty
        last_trade_price = trade_price

        qty -= trade_qty
        best.qty -= trade_qty

        if best.qty == 0:
            book.buys.pop(0)

    for p, q in trades.items():
        print(f"Trade, price: {p}, qty: {q}")