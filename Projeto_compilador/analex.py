import ply.lex as lex

tokens = [
    #palavras reservadas
    'PROGRAM', 'VAR', 'BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR',
    'TO', 'DOWNTO', 'OF', 'ARRAY', 'FUNCTION', 'PROCEDURE', 'CONST', 'TYPE' , 'RECORD', 'FORWARD', 'RETURN', #until repeat (decidir se metemos ou não)
                                                            #adicionado Const, type e record
    #tipos
    'STRING', 'INTEGER', 'CHAR', 'REAL', 'BOOLEAN', 'SET', 'FILE', #adicionado set e file

    #operadores
    'ADD', 'SUB', 'MUL', 'DIVIDE', 'EQUAL', 'NOTEQUAL', 'LESS', 'GREATER',
    'LESSEQUAL', 'GREATEREQUAL', 'AND', 'OR', 'NOT', 'DIV', 'MOD', 'POW', 'AT',
                                                            #adicionado o pow , at e caret (^) -> tirei o caret porque serve para fazer apontadores
    #delimitadores
    'COMMA', 'ASSIGN', 'COLON', 'SEMICOLON', 'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET', 'RANGE', "DOT",

    #literais
    'TRUE', 'FALSE', 'INTEGER_CONST','REAL_CONST', 'STRING_CONST', 'HEX_CONST', 'CHAR_CONST', 'ID',
                                                            #adicionado o hex_const e char_const
    #funções
    'WRITELN', 'READLN',

    #controlo (adicionado)
    'BREAK', 'EXIT', 'CONTINUE',

    #ainda tem o directive mas não sei o trabalho que isso iria dar
]

# Operadores (os mais longos primeiro)
t_ASSIGN = r':='
t_EQUAL = r'='
t_NOTEQUAL = r'<>'
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>='
t_LESS = r'<'
t_GREATER = r'>'
t_POW = r'\*\*'
t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIVIDE = r'/'
t_AT = r'@'

# Delimitadores
t_COMMA = r','
t_COLON = r':'
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_RANGE = r'\.\.'
t_DOT = r'\.'

def t_PROGRAM(t):
    r'\b(?i)program\b'
    t.type = 'PROGRAM'
    t.value = t.value.lower()
    return t

def t_VAR(t):
    r'\b(?i)var\b'
    t.type = 'VAR'
    t.value = t.value.lower()
    return t

def t_BEGIN(t):
    r'\b(?i)begin\b'
    t.type = 'BEGIN'
    t.value = t.value.lower()
    return t

def t_END(t):
    r'\b(?i)end\b'
    t.type = 'END'
    t.value = t.value.lower()
    return t

def t_IF(t):
    r'\b(?i)if\b'
    t.type = 'IF'
    t.value = t.value.lower()
    return t

def t_THEN(t):
    r'\b(?i)then\b'
    t.type = 'THEN'
    t.value = t.value.lower()
    return t

def t_ELSE(t):
    r'\b(?i)else\b'
    t.type = 'ELSE'
    t.value = t.value.lower()
    return t

def t_WHILE(t):
    r'\b(?i)while\b'
    t.type = 'WHILE'
    t.value = t.value.lower()
    return t

def t_DO(t):
    r'\b(?i)do\b'
    t.type = 'DO'
    t.value = t.value.lower()
    return t

def t_FOR(t):
    r'\b(?i)for\b'
    t.type = 'FOR'
    t.value = t.value.lower()
    return t

def t_TO(t):
    r'\b(?i)to\b'
    t.type = 'TO'
    t.value = t.value.lower()
    return t

def t_DOWNTO(t):
    r'\b(?i)downto\b'
    t.type = 'DOWNTO'
    t.value = t.value.lower()
    return t

def t_OF(t):
    r'\b(?i)of\b'
    t.type = 'OF'
    t.value = t.value.lower()
    return t

def t_ARRAY(t):
    r'\b(?i)array\b'
    t.type = 'ARRAY'
    t.value = t.value.lower()
    return t

def t_FUNCTION(t):
    r'\b(?i)function\b'
    t.type = 'FUNCTION'
    t.value = t.value.lower()
    return t

def t_PROCEDURE(t):
    r'\b(?i)procedure\b'
    t.type = 'PROCEDURE'
    t.value = t.value.lower()
    return t

def t_CONST(t):
    r'\b(?i)const\b'
    t.type = 'CONST'
    t.value = t.value.lower()
    return t

def t_TYPE(t):
    r'\b(?i)type\b'
    t.type = 'TYPE'
    t.value = t.value.lower()
    return t

def t_RECORD(t):
    r'\b(?i)record\b'
    t.type = 'RECORD'
    t.value = t.value.lower()
    return t

def t_SET(t):
    r'\b(?i)set\b'
    t.type = 'SET'
    t.value = t.value.lower()
    return t

def t_FILE(t):
    r'\b(?i)file\b'
    t.type = 'FILE'
    t.value = t.value.lower()
    return t

def t_STRING(t):
    r'\b(?i)string\b'
    t.type = 'STRING'
    t.value = t.value.lower()
    return t

def t_INTEGER(t):
    r'\b(?i)integer\b'
    t.type = 'INTEGER'
    t.value = t.value.lower()
    return t

def t_CHAR(t):
    r'\b(?i)char\b'
    t.type = 'CHAR'
    t.value = t.value.lower()
    return t

def t_REAL(t):
    r'\b(?i)real\b'
    t.type = 'REAL'
    t.value = t.value.lower()
    return t

def t_BOOLEAN(t):
    r'\b(?i)boolean\b'
    t.type = 'BOOLEAN'
    t.value = t.value.lower()
    return t

def t_AND(t):
    r'\b(?i)and\b'
    t.type = 'AND'
    t.value = t.value.lower()
    return t

def t_OR(t):
    r'\b(?i)or\b'
    t.type = 'OR'
    t.value = t.value.lower()
    return t

def t_NOT(t):
    r'\b(?i)not\b'
    t.type = 'NOT'
    t.value = t.value.lower()
    return t

def t_DIV(t):
    r'\b(?i)div\b'
    t.type = 'DIV'
    t.value = t.value.lower()
    return t

def t_MOD(t):
    r'\b(?i)mod\b'
    t.type = 'MOD'
    t.value = t.value.lower()
    return t

def t_TRUE(t):
    r'\b(?i)true\b'
    t.type = 'TRUE'
    t.value = t.value.lower()
    return t

def t_FALSE(t):
    r'\b(?i)false\b'
    t.type = 'FALSE'
    t.value = t.value.lower()
    return t

def t_WRITELN(t):
    r'\b(?i)writeln\b'
    t.type = 'WRITELN'
    t.value = t.value.lower()
    return t

def t_READLN(t):
    r'\b(?i)readln\b'
    t.type = 'READLN'
    t.value = t.value.lower()
    return t

def t_BREAK(t):
    r'\b(?i)break\b'
    t.type = 'BREAK'
    t.value = t.value.lower()
    return t

def t_EXIT(t):
    r'\b(?i)exit\b'
    t.type = 'EXIT'
    t.value = t.value.lower()
    return t

def t_CONTINUE(t):
    r'\b(?i)continue\b'
    t.type = 'CONTINUE'
    t.value = t.value.lower()
    return t

def t_FORWARD(t):
    r'\b(?i)forward\b'
    t.type = 'FORWARD'
    t.value = t.value.lower()
    return t

def t_RETURN(t):
    r'\b(?i)return\b'
    t.type = 'RETURN'
    t.value = t.value.lower()
    return t


def t_CHAR_CONST(t):
    r'\#\d+'
    t.value = chr(int(t.value[1:]))
    return t

def t_HEX_CONST(t):
    r'\$[0-9a-fA-F]+'
    t.value = int(t.value[1:], 16)
    return t

def t_REAL_CONST(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_CONST(t):
    r"'([^']|'')*'"
    t.value = t.value[1:-1].replace("''", "'")
    return t

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type =  'ID'
    t.value = t.value.lower()
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.column = 0

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

def t_comment(t):
    r'\{[^}]*\}|\(\*.*?\*\)|//.*'
    pass


def t_error(t):
    col = find_column(lexer.lexdata, t)
    print(f"Erro léxico na linha {t.lineno}, coluna {col}: Caractere inválido '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()


