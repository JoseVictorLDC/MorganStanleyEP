# Exercício de Programa – Morgan Stanley

**Matching Engine** em Python para um único ativo.  

---

## Documentação acerca do projeto

Acesse o pdf com as especificações de projeto.<br>
[Clique aqui para abrir o PDF](MorganStanleyEP.pdf)

---

## Estrutura do projeto

```text
MorganStanleyEP/
├── src/
│   ├── app.py          # interface de linha de comando
│   ├── book.py         # OrderBook e estado do livro
│   ├── limit.py        # lógica de ordens limit
│   ├── market.py       # lógica de ordens a mercado
│   └── pegged.py       # lógica de ordens pegged
│
├── requirements.txt    # dependências do projeto
└── README.md           # documentação do projeto
```
---

## Como rodar

```bash
# 1. Clonar o repositório
git clone https://github.com/JoseVictorLDC/MorganStanleyEP.git
cd MorganStanleyEP

# 2. (Opcional) instalar dependências
python -m pip install -r requirements.txt

# 3. Entrar na pasta
cd .\src\

# 4. Executar o APP
python app.py
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
