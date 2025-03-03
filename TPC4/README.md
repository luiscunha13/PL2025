# TPC4

## 03/03/2024

## Autor
- Luís Cunha
- a104613

## Informações sobre o TPC4

O TPC4 consistia em construir um analisador léxico para uma liguagem de query com a qual se podem escrever frases do
género:

```
# DBPedia: obras de Chuck Berry

select ?nome ?desc where {
    ?s a dbo:MusicalArtist.
    ?s foaf:name "Chuck Berry"@en .
    ?w dbo:artist ?s.
    ?w foaf:name ?nome.
    ?w dbo:abstract ?desc
} LIMIT 1000
```

## Desenvolvimento
Primeiramente foi necessário definir os tokens, juntamente com os regex que os identificam.
De seguida, foi usada a biblioteca ply.tex de forma a encontrar os tokens ao longo do texto

## Execução
Programa: [analisador.py](https://github.com/luiscunha13/PL2025/tree/main/TPC4/analisador.py)

Execução: `python3 analisador.py`