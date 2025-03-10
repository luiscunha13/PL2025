# TPC5

## 10/03/2024

## Autor
- Luís Cunha
- a104613

## Informações sobre o TPC5

O TPC5 consistia em construir um programa que simule uma máquina de vending
A máquina tem um stock de produtos: código, nome do produto, quantidade e preço.

```
stock = [
{"cod": "A23", "nome": "água 0.5L", "quant": 8, "preco": 0.7},
...
]
```

Exemplo de interação:

```
maq: 2024-03-08, Stock carregado, Estado atualizado.
maq: Bom dia. Estou disponível para atender o seu pedido.
>> LISTAR
maq:
cod | nome | quantidade | preço
---------------------------------
A23 água 0.5L 8 0.7
...
>> MOEDA 1e, 20c, 5c, 5c .
maq: Saldo = 1e30c
>> SELECIONAR A23
maq: Pode retirar o produto dispensado "água 0.5L"
maq: Saldo = 60c
>> SELECIONAR A23
maq: Saldo insufuciente para satisfazer o seu pedido
maq: Saldo = 60c; Pedido = 70c
>> ...
...
maq: Saldo = 74c
>> SAIR
maq: Pode retirar o troco: 1x 50c, 1x 20c e 2x 2c.
maq: Até à próxima
```

## Desenvolvimento
Primeiramente foi necessário definir o stock num ficheiro JSON
De seguida, defini os tokens, juntamente com os regex que os identificam.
Para cada tipo de comando foi preciso criar uma função que o processasse.
Tipos de comando: listar, moeda, selecionar, sair

## Execução
Ficheiro JSON: [stock.json](https://github.com/luiscunha13/PL2025/tree/main/TPC5/stock.json)

Programa: [vendingMachine.py](https://github.com/luiscunha13/PL2025/tree/main/TPC5/vendingMachine.py)

Execução: `python3 vendingMachine.py`