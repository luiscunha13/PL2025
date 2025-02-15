import sys

def somadorOnOff(l):
    on = True
    acc=0
    i=0
    valor=0

    while i < len(l):
        if l[i].isdigit() and on:
            while l[i].isdigit() and on:
                valor = valor * 10 + int(l[i])
                i+=1

            acc+= valor
            valor=0

        elif l[i:i+2].lower()=='on':
            on = True
            i+=1

        elif l[i:i+3].lower()=='off':
            on = False
            i+=2

        elif l[i]=='=':
            print(acc)

        i+=1

    if valor!=0 and on:
        acc+=valor

    print(f"Final = {acc}")

for line in sys.stdin:
    somadorOnOff(line)
