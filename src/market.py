# src/market.py
# Processa uma ordem market de compra
def match_market_buy(book, qty: int, ts: int):
    i = 0
    sells = book.sells 
    while qty > 0 and i < len(sells):
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

# Processa uma ordem market de venda
def match_market_sell(book, qty: int, ts: int):
    i = 0
    buys = book.buys  
    while qty > 0 and i < len(buys):
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
