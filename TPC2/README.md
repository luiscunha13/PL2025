# TPC2

## 15/02/2024

## Autor
- Luís Cunha
- a104613

## Informações sobre o TPC2

O TPC2 consistia em analisar um dataset de obras musicais e processá-lo de forma a ter os seguintes resultados:
- Lista ordenada alfabeticamente dos compositores musicais;
- Distribuição das obras por período: quantas obras catalogadas em cada período;
- Dicionário em que a cada período está a associada uma lista alfabética dos títulos das obras desse período.

Restrição: proibido usar o módulo CSV do Python.

## Desenvolvimento
O programa tem de analisar o ficheiro obras.csv que tem delimitador ';'. 
No entanto, no campo da descrição dentro de aspas é possível ter ';' que não sejam delimitadores. 
Para além disso, existem '\n' que dividem as linhas em várias.
Tendo em conta estes detalhes, foi necessário criar um acc para contar os campos já preenchidos e um boolean aspas que indica se estamos  a analisar texto dentro de aspas.
Também foi criada uma lista para os compositores, um dicionário para os as obras de cada período e um dicionário para os dados divididos de cada linha.
O programa lê o stdin que é o ficheiro csv, ignora a primeira linha por ser o cabeçalho e para as restantes linhas lê um char de cada vez. 
Se o char for '"' coloca o boolean aspas a True/False (dependendo do seu valor anterior), se o char for ';' e aspas=False (o ';' é delimitador), o valor é adicionado ao dicionário dos dados e o acc é incrementado.
No final da linha adiciona o valor atual ao dados[acc]. Quando o acc == 6 (todos os campos estão carregados), retira-se os dados necessários e adiciona-se às estruturas criadas para os guardar.
No final de carregar todas as linhas, consulta-se a lista dos compositores e o dicionário das obras por período, ordenam-se os dados alfabeticamente e exibem-se os resultados.

## Execução
Ficheiro csv: [obras.csv](https://github.com/luiscunha13/PL2025/tree/main/TPC2/obras.csv)

Programa: [parser.py](https://github.com/luiscunha13/PL2025/tree/main/TPC2/parser.py)

Execução: `python3 parser.py < obras.csv`