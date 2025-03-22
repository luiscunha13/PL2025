from analex import lexer

prox_simb = ('Erro', '', 0, 0)

def parserError(simb):
    print("Erro sintático, token inesperado: ", simb)

def rec_Exp():
    print("Derivando por: Exp --> Termo Exp2")
    l = rec_Termo()
    r = rec_Exp2(l)
    print("Reconheci: Exp --> Termo Exp2")
    return r

def rec_Exp2(l):
    global prox_simb
    if prox_simb is None:
        return l
    elif prox_simb.type == 'ADD':
        print("Derivando por: Exp2 --> '+' Termo Exp2")
        rec_term('ADD')
        t = rec_Termo()
        res = rec_Exp2(l + t)
        print("Reconheci: Exp2 --> '+' Termo Exp2")
        return res
    elif prox_simb.type == 'SUB':
        print("Derivando por: Exp2 --> '-' Termo Exp2")
        rec_term('SUB')
        t = rec_Termo()
        res = rec_Exp2(l - t)
        print("Reconheci: Exp2 --> '-' Termo Exp2")
        return res
    elif prox_simb.type == 'FP':
        print("Derivando por: Exp2 --> ε")
        print("Reconheci: Exp2 --> ε")
        return l
    else:
        parserError(prox_simb)
        return l

def rec_Termo():
    print("Derivando por: Termo --> Fator Termo2")
    l = rec_Fator()
    r = rec_Termo2(l)
    print("Reconheci: Termo --> Fator Termo2")
    return r

def rec_Termo2(l):
    global prox_simb
    if prox_simb is None:
        return l
    elif prox_simb.type == 'MUL':
        print("Derivando por: Termo2 --> '*' Fator Termo2")
        rec_term('MUL')
        f = rec_Fator()
        r = rec_Termo2(l * f)
        print("Reconheci: Termo2 --> '*' Fator Termo2")
        return r
    elif prox_simb.type == 'DIV':
        print("Derivando por: Termo2 --> '/' Fator Termo2")
        rec_term('DIV')
        f = rec_Fator()
        if f == 0:
            print("Aviso: Divisão por zero")
            return float('inf')
        r = rec_Termo2(l / f)
        print("Reconheci: Termo2 --> '/' Fator Termo2")
        return r
    elif prox_simb.type in ('ADD', 'SUB', 'FP'):
        print("Derivando por: Termo2 --> ε")
        print("Reconheci: Termo2 --> ε")
        return l
    else:
        parserError(prox_simb)
        return l

def rec_Fator():
    global prox_simb
    if prox_simb is None:
        return 0
    elif prox_simb.type == 'AP':
        print("Derivando por: Fator --> '(' Exp ')'")
        rec_term('AP')
        e = rec_Exp()
        rec_term('FP')
        print("Reconheci: Fator --> '(' Exp ')'")
        return e
    elif prox_simb.type == 'NUM':
        print("Derivando por: Fator --> NUM")
        n = float(prox_simb.value)
        rec_term('NUM')
        print("Reconheci: Fator --> NUM")
        return n
    else:
        parserError(prox_simb)
        return 0

def rec_term(simb):
    global prox_simb
    if prox_simb is None:
        return
    elif prox_simb.type == simb:
        prox_simb = lexer.token()
    else:
        parserError(prox_simb)

def rec_Parser(data):
    global prox_simb
    lexer.input(data)
    prox_simb = lexer.token()
    result = rec_Exp()
    return result