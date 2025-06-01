
## Exemplo 1

### Input

```pascal
program HelloWorld;
begin
writeln('Ola, Mundo!');
end.
```

### Resultado

```asm
// Program: helloworld
START
PUSHS "Ola, Mundo!"
WRITES
WRITELN
stop
```

---

## Exemplo 2

### Input

```pascal
program Fatorial;
var
n, i, fat: integer;
begin
writeln('Introduza um número inteiro positivo:');
readln(n);
fat := 1;
for i := 1 to n do
fat := fat * i;
writeln('Fatorial de ', n, ': ', fat);
end.
```

### Resultado

```asm
// Program: fatorial
START
PUSHS "Introduza um número inteiro positivo:"
WRITES
WRITELN
READ
ATOI
STOREG 0
PUSHI 1
STOREG 2
PUSHI 1
STOREG 1
LoopCondition0:
PUSHG 1
PUSHG 0
INFEQ
JZ LoopEnd1
PUSHG 2
PUSHG 1
MUL
STOREG 2
PUSHG 1
PUSHI 1
ADD
STOREG 1
JUMP LoopCondition0
LoopEnd1:
PUSHS "Fatorial de "
WRITES
PUSHG 0
WRITEI
PUSHS ": "
WRITES
PUSHG 2
WRITEI
WRITELN
stop
```

---

## Exemplo 3

### Input

```pascal
program NumeroPrimo;
var
num, i: integer;
primo: boolean;
begin
writeln('Introduza um número inteiro positivo:');
readln(num);
primo := true;
i := 2;
while (i <= (num div 2)) and primo do
begin
if (num mod i) = 0 then
primo := false;
i := i + 1;
end;
if primo then
writeln(num, ' é um número primo')
else
writeln(num, ' não é um número primo')
end.
```

### Resultado

```asm
// Program: numeroprimo
START
PUSHS "Introduza um número inteiro positivo:"
WRITES
WRITELN
READ
ATOI
STOREG 0
PUSHI 1
STOREG 2
PUSHI 2
STOREG 1
WHILESTART0:
PUSHG 1
PUSHG 0
PUSHI 2
DIV
INFEQ
PUSHG 2
AND
JZ WHILEEND1
PUSHG 0
PUSHG 1
MOD
PUSHI 0
EQUAL
JZ ENDIF2
PUSHI 0
STOREG 2
ENDIF2:
PUSHG 1
PUSHI 1
ADD
STOREG 1
JUMP WHILESTART0
WHILEEND1:
PUSHG 2
JZ ELSE3
PUSHG 0
WRITEI
PUSHS " é um número primo"
WRITES
WRITELN
JUMP ENDIF4
ELSE3:
PUSHG 0
WRITEI
PUSHS " não é um número primo"
WRITES
WRITELN
ENDIF4:
stop
```

---

## Exemplo 4

### Input

```pascal
program SomaArray;
var
numeros: array[1..5] of integer;
i, soma: integer;
begin
soma := 0;
writeln('Introduza 5 números inteiros:');
for i := 1 to 5 do
begin
readln(numeros[i]);
soma := soma + numeros[i];
end;
writeln('A soma dos números é: ', soma);
end.
```

### Resultado

```asm
// Program: somaarray
START
pushi 5
allocn
storeg 0
PUSHI 0
STOREG 2
PUSHS "Introduza 5 números inteiros:"
WRITES
WRITELN
PUSHI 1
STOREG 1
LoopCondition0:
PUSHG 1
PUSHI 5
INFEQ
JZ LoopEnd1
READ
ATOI
PUSHG 0
PUSHG 1
PUSHI 1
SUB
PADD
SWAP
STORE 0
PUSHG 2
PUSHG 0
PUSHG 1
PUSHI 1
SUB
PADD
LOAD 0
ADD
STOREG 2
PUSHG 1
PUSHI 1
ADD
STOREG 1
JUMP LoopCondition0
LoopEnd1:
PUSHS "A soma dos números é: "
WRITES
PUSHG 2
WRITEI
WRITELN
stop
```

---

## Exemplo 5

### Input

```pascal
program BinarioParaInteiro;
function BinToInt(bin: string): integer;
var
i, valor, potencia: integer;
begin
valor := 0;
potencia := 1;
for i := length(bin) downto 1 do
begin
if bin[i] = '1' then
valor := valor + potencia;
potencia := potencia * 2;
end;
BinToInt := valor;
end;
var
bin: string;
valor: integer;
begin
writeln('Introduza uma string binária:');
readln(bin);
valor := BinToInt(bin);
writeln('O valor inteiro correspondente é: ', valor);
end.
```

### Resultado

```asm
// Program: binarioparainteiro
START
PUSHS "Introduza uma string binária:"
WRITES
WRITELN
READ
STOREG 0
PUSHG 0
PUSHA bintoint
CALL
STOREG 1
PUSHS "O valor inteiro correspondente é: "
WRITES
PUSHG 1
WRITEI
WRITELN
stop

// Function bintoint
bintoint:
PUSHN 3
PUSHI 0
STOREL 1
PUSHI 1
STOREL 2
PUSHL -1
STRLEN
STOREL 0
LoopCondition0:
PUSHL 0
PUSHI 1
SUPEQ
JZ LoopEnd1
PUSHL -1
PUSHL 0
PUSHI 1
SUB
CHARAT
PUSHI 49
EQUAL
JZ ENDIF2
PUSHL 1
PUSHL 2
ADD
STOREL 1
ENDIF2:
PUSHL 2
PUSHI 2
MUL
STOREL 2
PUSHL 0
PUSHI 1
SUB
STOREL 0
JUMP LoopCondition0
LoopEnd1:
PUSHL 1
RETURN
```
