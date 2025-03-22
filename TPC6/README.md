# TPC6

## 22/03/2024

## Autor
- Luís Cunha
- a104613

## Informações sobre o TPC6

O TPC6 consistia em criar um parser LL(1) recursivo descendente que reconheça expressões aritméticas e calcule o respetivo valor.

Exemplos:

```
    2+3
    67-(2+3*4)
    (9-2)*(13-4)
```

## Desenvolvimento
Primeiramente foi necessário definir os tokens no *analex.py*.
De seguida, a gramática foi definida no *anasin.py* da seguinte forma:

```
    Exp --> Termo Exp2
    
    Exp2 --> '+' Termo Exp2
           | '-' Termo Exp2
           | ε
           
    Termo --> Fator Termo2
    
    Termo2 --> '*' Fator Termo
             | '/' Fator Termo
             | ε
    
    Fator --> '(' Exp ')'
            | num
```

## Execução

Analex: [analex.py](https://github.com/luiscunha13/PL2025/tree/main/TPC6/analex.py)

Anasin: [anasin.py](https://github.com/luiscunha13/PL2025/tree/main/TPC6/anasin.py)

Programa: [program.py](https://github.com/luiscunha13/PL2025/tree/main/TPC6/program.py)

Execução: `python3 program.py`