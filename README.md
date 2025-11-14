# Exercício de Programa – Morgan Stanley

Mini **Matching Engine** em Python para um único ativo, suportando:

- Ordens **limit** (compra/venda)
- Ordens **market**
- Ordens **pegged** ao melhor **bid** ou **offer**
- Cancelamento de ordens
- Modificação de ordens
- Visualização do livro de ofertas em formato de tabela no terminal

---

## Estrutura do projeto

morgan-matching-engine/
├─ src/
│  ├─ models.py       # dataclass Order
│  ├─ order_book.py   # classe OrderBook e toda lógica de matching
│  └─ cli.py          # interface de linha de comando (process_line + main)
├─ requirements.txt   # dependências (somente Python padrão)
└─ README.md

---

## Como rodar

1. **Instale o Python 3.10+**  
   No Windows:  
   https://www.python.org/downloads/windows/  

   Marque na instalação:  
   `Add python.exe to PATH`

2. **Clone o repositório**:

   git clone https://github.com/<seu-usuario>/morgan-matching-engine.git
   cd morgan-matching-engine

3. **(Opcional) Instale dependências**  
   O projeto não usa bibliotecas externas além da stdlib, mas para manter o padrão:

   python -m pip install -r requirements.txt

4. **Execute o programa**:

   python -m src.cli

   ou

   python src/cli.py

5. Ao rodar, você verá algo como:

====================================================================
              Exercício de Programa da Morgan Stanley
                  Order Matching System (1 ativo)
====================================================================
Comandos básicos:
  limit          <buy/sell> <preço> <qty>      -> ordem limite
  market         <buy/sell> <qty>              -> ordem a mercado
  peg            <bid/offer> <buy/sell> <qty>  -> ordem pegged
  modify order   <id> <qty>                    -> altera qty de peg
  modify order   <id> <preço> <qty>            -> altera limit
  cancel order   <id>                          -> cancela ordem
  print book                                   -> mostra o livro
  exit                                         -> sai do programa
====================================================================
>>>

---

## Comandos suportados

### 1. `limit` — ordem limite

Sintaxe:

    limit <buy/sell> <preço> <qty>

Exemplos:

    limit buy 10 100
    limit sell 20.5 50

---

### 2. `market` — ordem a mercado

Sintaxe:

    market <buy/sell> <qty>

Exemplos:

    market buy 150
    market sell 80

---

### 3. `peg` — ordem pegged

Uma ordem pegged segue sempre o melhor bid ou o melhor offer.

Sintaxe:

    peg <bid/offer> <buy/sell> <qty>

- `peg bid buy <qty>`  → ordem de compra atrelada ao melhor bid
- `peg offer sell <qty>` → ordem de venda atrelada ao melhor offer

Exemplos:

    peg bid buy 100
    peg offer sell 75

---

### 4. `modify order` — modificar ordem pegged (somente quantidade)

Para ordens pegged, só faz sentido alterar a quantidade; o preço é atualizado automaticamente pelo engine.

Sintaxe:

    modify order <id> <qty>

Exemplo:

    modify order identificador_7 40

---

### 5. `modify order` — modificar ordem limit normal

Para ordens limit “normais”, é possível alterar preço e quantidade.  
Ao alterar, a ordem perde prioridade temporal (ganha novo timestamp).

Sintaxe:

    modify order <id> <preço> <qty>

Exemplo:

    modify order identificador_4 9.98 200

---

### 6. `cancel order` — cancelar ordem ativa

Cancela uma ordem limit (normal ou pegged) ainda ativa no livro.

Sintaxe:

    cancel order <id>

Exemplos:

    cancel order identificador_1
    cancel order identificador_8

---

### 7. `print book` — exibir o livro

Mostra todas as ordens de compra e venda em uma tabela ASCII:

    print book

Saída típica:

    +-------------------+-------------------+
    | Ordens de Compra  | Ordens de Venda   |
    +-------------------+-------------------+
    | 200 @ 10.0        | 100 @ 10.5        |
    | 100 @ 9.99        |                   |
    +-------------------+-------------------+

---

### 8. `exit` — sair

Encerra o programa:

    exit

ou

    quit

---

## Prioridade e Regras

- **Compras (book de bids)**  
  - Preço maior tem prioridade.  
  - Com o mesmo preço, a ordem com menor timestamp (chegou antes) vem primeiro.

- **Vendas (book de offers)**  
  - Preço menor tem prioridade.  
  - Com o mesmo preço, a ordem com menor timestamp vem primeiro.

- **Execução (matching)**  
  - `limit buy` cruza contra os melhores `sell` com preço `<=` ao preço da ordem.  
  - `limit sell` cruza contra os melhores `buy` com preço `>=` ao preço da ordem.  
  - `market buy` consome vendedores do melhor preço para cima até zerar a quantidade ou esvaziar o book de venda.  
  - `market sell` consome compradores do melhor preço para baixo até zerar a quantidade ou esvaziar o book de compra.  
  - Cada trade é impresso como:

        Trade, price: <preço>, qty: <quantidade>

- **Pegged (bid/offer)**  
  - `peg bid buy` toma como referência o melhor bid **limit normal** (não pegged).  
  - `peg offer sell` toma como referência o melhor offer **limit normal**.  
  - Quando o bid/offer de referência sobe ou desce, a ordem pegged:
    - tem o preço atualizado para o novo melhor bid/offer;
    - recebe um novo timestamp lógico (perde prioridade temporal).
  - Se não houver mais nenhuma ordem limit normal que sirva de referência:
    - As ordens pegged correspondentes são **canceladas automaticamente** e é impresso:

          Pegged order cancelled (no bid reference) <id>
          Pegged order cancelled (no offer reference) <id>

---

## Exemplo rápido de fluxo

1. Cria uma ordem limit de compra:

       limit buy 10 100
       -> Order created: buy 100 @ 10.0 identificador_1

2. Cria uma ordem pegged ao bid:

       peg bid buy 50
       -> Pegged order created: buy 50 @ 10.0 (peg to bid) identificador_2

3. Entra uma ordem market de venda:

       market sell 120
       -> Trade, price: 10.0, qty: 120

4. Imprime o livro:

       print book

---

## Observações

- O objetivo é demonstrar conceitos de um matching engine real de forma simples.
- Todo o estado é mantido apenas em memória.
- O código é modularizado em:
  - `models.py` → definição da `Order`
  - `order_book.py` → lógica de matching, cancel, modify, peg, etc.
  - `cli.py` → loop de terminal, parsing de comandos e integração com o `OrderBook`.