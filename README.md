# Exercício de Programa – Morgan Stanley

Mini **Matching Engine** em Python para um único ativo.  
Objetivo: receber ordens de compra e venda via terminal, cruzá-las de forma justa e mostrar o livro de ofertas.

---

## Estrutura do projeto

morgan-matching-engine/
├─ src/
│  ├─ models.py       # dataclass Order
│  ├─ order_book.py   # classe OrderBook e lógica de matching
│  └─ cli.py          # interface de linha de comando (loop do terminal)
├─ requirements.txt   # dependências (apenas stdlib, mantido por padrão)
└─ README.md

---

## Como rodar

1. Instalar Python 3.10+ (marcar “Add python.exe to PATH” no Windows).
2. Clonar o repositório:

   git clone https://github.com/<seu-usuario>/morgan-matching-engine.git
   cd morgan-matching-engine

3. (Opcional) instalar dependências:

   python -m pip install -r requirements.txt

4. Executar o CLI:

   python -m src.cli
   # ou
   python src/cli.py

---

## Comandos principais do sistema

Todos os comandos são digitados no prompt `>>>`.

- Ordem **limit**:

    limit <buy/sell> <preço> <qty>

- Ordem **market**:

    market <buy/sell> <qty>

- Ordem **pegged** (segue melhor bid/offer):

    peg <bid/offer> <buy/sell> <qty>

- Modificar **ordem pegged** (só quantidade):

    modify order <id> <qty>

- Modificar **ordem limit** (preço e quantidade):

    modify order <id> <preço> <qty>

- Cancelar ordem:

    cancel order <id>

- Mostrar livro de ofertas:

    print book

- Sair do programa:

    exit
    quit