# TPC3

## 25/02/2024

## Autor
- Luís Cunha
- a104613

## Informações sobre o TPC2

O TPC2 consistia em criar um conversor de MarkDown para HTML capaz de converter cabeçalhos, bold, itálico, listas numeradas, links e imagens.



## Desenvolvimento
Para cada um dos casos foi criado um regex que caso desse match alteraria o texto para o converter para html. 
Este processo é feito linha a linha. 
A única exceção tratada de forma diferente dá-se quando se tem de incluir o <ol> e o </ol> para delimitar uma lista. 
Neste caso é necessário analisar todas as linhas.

## Execução
Ficheiro markdown: [markdown.txt](https://github.com/luiscunha13/PL2025/tree/main/TPC3/markdown.txt)

Programa: [converter.py](https://github.com/luiscunha13/PL2025/tree/main/TPC3/converter.py)

Execução: `python3 converter.py markdown.txt`