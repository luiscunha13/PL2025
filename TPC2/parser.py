import sys

compositores = []
map_obras_periodo = {}
dados = {}
acc=0
aspas=False

next(sys.stdin)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    field = ""
    for char in line:
        if char == '"':
            aspas = not aspas
        elif char == ';' and not aspas:
            if acc not in dados.keys():
                dados[acc] = field.strip()
                dados[acc] += " "
            else:
                dados[acc] += field.strip()
                dados[acc] += " "

            acc+=1
            field = ""
        else:
            field += char

    if acc not in dados.keys():
        dados[acc] = field.strip()
        dados[acc] += " "
    else:
        dados[acc] += field.strip()
        dados[acc] += " "

    if acc == 6:
        acc = 0
        aspas = False

        obra = dados[0]
        periodo = dados[3]
        compositor = dados[4]

        if compositor not in compositores:
            compositores.append(compositor)

        if periodo not in map_obras_periodo:
            map_obras_periodo[periodo] = []

        if obra not in map_obras_periodo[periodo]:
            map_obras_periodo[periodo].append(obra)

        dados = {}


print("--Resultados--\n")

print("Compositores ordenados alfabeticamente:\n")
compositores.sort()
for compositor in compositores:
    print(compositor)

print("\nNúmero obras por período:\n")
for periodo in map_obras_periodo:
    print(f"{periodo}: {len(map_obras_periodo[periodo])}")

print("\nObras por período:\n")
for periodo in map_obras_periodo:
    print(f"{periodo}:")
    obras_ordenadas = sorted(map_obras_periodo[periodo])
    for obra in obras_ordenadas:
        print(f"  - {obra}")





