import json
import ply.lex as lex
import datetime

stock = []
money = 0

moedas = {
    "2e": 2.00,
    "1e": 1.00,
    "50c": 0.50,
    "20c": 0.20,
    "10c": 0.10,
    "5c": 0.05,
    "2c": 0.02,
    "1c": 0.01
}

tokens = [
    "LISTAR",
    "ADDMOEDA",
    "MOEDA",
    "SELECIONAR",
    "ADICIONAR",
    "PRODUTO",
    "VIRGULA",
    "PONTO",
    "SAIR",
    "INVALID"
]


# Define regular expressions for tokens
def t_LISTAR(t):
    r'(?i)listar'
    return t


def t_ADDMOEDA(t):
    r'(?i)moeda'
    return t


def t_MOEDA(t):
    r'\d+[ec]'
    return t


def t_SELECIONAR(t):
    r'(?i)selecionar'
    return t


def t_PRODUTO(t):
    r'[A-Z]\d+'
    return t


def t_VIRGULA(t):
    r','
    return t


def t_PONTO(t):
    r'\.'
    return t


def t_SAIR(t):
    r'(?i)sair'
    return t


def t_INVALID(t):
    r'[^\s,.]+'
    return t


t_ignore = ' \t\n'


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


def loadStock():
    global stock
    try:
        with open('stock.json', 'r') as json_file:
            stock = json.load(json_file)
            return True
    except:
        return False


def listProducts():
    print("map:")
    print("cod  |  nome  |  quantidade  |  preço")
    print("---------------------------------")
    for product in stock:
        print(f"{product['cod']}  {product['nome']}  {product['quant']}  {product['preco']}")


def printMoney(money):
    if money < 1:
        return f"{int(money * 100)}c"
    if money.is_integer():
        return f"{int(money)}e"
    else:
        int_part, decimal_part = str(money).split(".")
        return f"{int_part}e{int(decimal_part)*10}c"


def insertCoins(lexer):
    global money
    valid_coins = list(moedas.keys())

    for token in lexer:
        if token.type == "MOEDA":
            value = token.value
            if value in valid_coins:
                money += moedas[value]
            else:
                print(f"maq: Moeda inválida: {value}")
        elif token.type == "VIRGULA" or token.type == "PONTO":
            continue
        else:
            print(f"maq: Moeda inválida: {token.value}")

    print(f"Saldo = {printMoney(round(money, 2))}")


def selectProduct(lexer):
    global stock
    global money

    token = lexer.token()
    if token is None:
        print("maq: Produto não especificado")
        return

    if token.type == "PRODUTO":
        product_code = token.value
        product_found = False

        for product in stock:
            if product['cod'] == product_code:
                product_found = True
                if product['quant'] > 0:
                    if money >= product['preco']:
                        product['quant'] -= 1
                        money -= product['preco']
                        print("maq: Recolha o produto")
                        print(f"Saldo = {printMoney(round(money, 2))}")
                    else:
                        print("maq: Saldo insuficiente para satisfazer pedido")
                        print(f"maq: Saldo = {printMoney(round(money, 2))}: Pedido = {product['preco']}")
                else:
                    print(f"maq: Produto indisponível: {product_code}")
                break

        if not product_found:
            print(f"maq: Produto inválido: {product_code}")
    else:
        print(f"maq: Produto inválido: {token.value}")


def exit():
    global money
    money_rounded = round(money, 2)

    change = []

    for coin, value in moedas.items:
        num_coins = int(money_rounded // value)
        if num_coins > 0:
            money_rounded -= num_coins * value
            money_rounded = round(money_rounded, 2)
            change.append(f"{num_coins}x {coin}")

    if len(change) > 1:
        print("maq: Pode retirar o troco: " + ", ".join(change[:-1]) + " e " + change[-1] + ".")
    elif change:
        print("maq: Pode retirar o troco: " + change[0] + ".")
    else:
        print("maq: Pode retirar o troco: 0c")

    # Reset money
    money = 0


def main():
    if loadStock():
        print(f"maq: {datetime.date.today()}, Stock carregado, Estado atualizado.")
        print("maq: Bom dia. Estou disponível para atender o seu pedido.")
    else:
        print("maq: Erro a carregar ficheiro JSON")

    working = True
    lexer = lex.lex()

    while working:
        command = input(">> ")
        lexer.input(command)
        token = lexer.token()

        if token is None:
            print("maq: Comando inválido")
            continue

        if token.type == "SAIR":
            exit()
            working = False
        elif token.type == "LISTAR":
            listProducts()
        elif token.type == "ADDMOEDA":
            insertCoins(lexer)
        elif token.type == "SELECIONAR":
            selectProduct(lexer)
        else:
            print(f"maq: Comando inválido: {token.value}")


if __name__ == "__main__":
    main()