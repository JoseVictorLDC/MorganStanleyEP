# src/cli.py
from .order_book import OrderBook

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
        if len(parts) != 3:
            print("Uso: market <buy/sell> <qty>")
            return
        _, side, qty = parts
        side = side.lower()
        qty = int(qty)
        book.handle_market(side, qty)
        return

    if cmd == "cancel":
        if len(parts) != 3 or parts[1].lower() != "order":
            print("Uso: cancel order <id>")
            return
        order_id = parts[2]
        book.cancel_order(order_id)
        return

    if cmd == "modify":
        # 1) modify order <id> <qty>            -> PEGGED
        # 2) modify order <id> <price> <qty>    -> LIMIT normal
        if len(parts) < 4 or parts[1].lower() != "order":
            print("Uso: modify order <id> <qty>  OU  modify order <id> <price> <qty>")
            return

        if len(parts) == 4:
            _, _, order_id, qty = parts
            qty = int(qty)
            book.modify_order_qty_only(order_id, qty)
            return

        if len(parts) == 5:
            _, _, order_id, price, qty = parts
            price = float(price)
            qty = int(qty)
            book.modify_order(order_id, price, qty)
            return

        print("Uso: modify order <id> <qty>  OU  modify order <id> <price> <qty>")
        return

    if cmd == "peg":
        if len(parts) != 4:
            print("Uso: peg <bid/offer> <buy/sell> <qty>")
            return
        _, reference, side, qty = parts
        qty = int(qty)
        book.handle_peg(reference, side, qty)
        return

    print("\nComando desconhecido.")
    print("=" * 68)
    print("Comandos básicos:")
    print("  limit          <buy/sell> <preço> <qty>      -> ordem limite")
    print("  market         <buy/sell> <qty>              -> ordem a mercado")
    print("  peg            <bid/offer> <buy/sell> <qty>  -> ordem pegged")
    print("  modify order   <id> <qty>                    -> altera qty de peg")
    print("  modify order   <id> <preço> <qty>            -> altera limit")
    print("  cancel order   <id>                          -> cancela ordem")
    print("  print book                                   -> mostra o livro")
    print("  exit                                         -> sai do programa")
    print("=" * 68)

def main():
    book = OrderBook()

    print("=" * 68)
    print("              Exercício de Programa da Morgan Stanley")
    print("                  Order Matching System (1 ativo)")
    print("=" * 68)
    print("Comandos básicos:")
    print("  limit          <buy/sell> <preço> <qty>      -> ordem limite")
    print("  market         <buy/sell> <qty>              -> ordem a mercado")
    print("  peg            <bid/offer> <buy/sell> <qty>  -> ordem pegged")
    print("  modify order   <id> <qty>                    -> altera qty de peg")
    print("  modify order   <id> <preço> <qty>            -> altera limit")
    print("  cancel order   <id>                          -> cancela ordem")
    print("  print book                                   -> mostra o livro")
    print("  exit                                         -> sai do programa")
    print("=" * 68)

    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break
        try:
            process_line(book, line)
        except SystemExit:
            break


if __name__ == "__main__":
    main()