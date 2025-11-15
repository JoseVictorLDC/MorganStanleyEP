# Exercício de Programa – Morgan Stanley

Mini **Matching Engine** em Python para um único ativo.  
Objetivo: receber ordens de compra e venda via terminal, cruzá-las de forma justa e mostrar o livro de ofertas.

---

## Estrutura do projeto

```text
MorganStanleyEP/
├── src/
│   ├── models.py       # dataclass Order
│   ├── order_book.py   # OrderBook e lógica de matching
│   └── cli.py          # interface de linha de comando (CLI)
│
├── requirements.txt    # dependências (padrão: apenas stdlib)
└── README.md
```
---

## Como rodar

```bash
# 1. Instalar Python 3.10+
#    (no Windows marcar: "Add python.exe to PATH")

# 2. Clonar o repositório
git clone https://github.com/JoseVictorLDC/MorganStanleyEP.git
cd MorganStanleyEP

# 3. (Opcional) instalar dependências
python -m pip install -r requirements.txt

# 4. Executar o CLI
python -m src.cli
# ou
python src/cli.py
```
---

## Comandos principais do sistema

Comandos disponíveis

Ordem limit:
```bash
limit <buy/sell> <preço> <qty>
```

Ordem market:
```bash
market <buy/sell> <qty>
```

Ordem pegged:
```bash
peg <bid/offer> <buy/sell> <qty>
```

Modificar ordem pegged (somente quantidade):
```bash
modify order <id> <qty>
```

Modificar ordem limit (preço e quantidade):
```bash
modify order <id> <preço> <qty>
```

Cancelar ordem:
```bash
cancel order <id>
```

Mostrar livro de ofertas:
```bash
print book
```

Sair do programa:
```bash
exit
```
```bash
quit
```

