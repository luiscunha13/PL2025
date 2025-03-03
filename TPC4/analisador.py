import ply.lex as lex

tokens = (
    'SELECT',
    'LIMIT',
    'WHERE',
    'COMMENT',
    'NUMBER',
    'VARIABLE',
    'URI',
    'LANG',
    'A',
    'DOT',
    'RBRACKET',
    'LBRACKET'
)

t_SELECT = r'(?i)select'
t_LIMIT = r'(?i)limit'
t_WHERE = r'(?i)where'
t_COMMENT = r'\#.*'
t_VARIABLE = r'\?[a-z]+'
t_URI = r'[a-zA-Z0-9]+:[a-zA-Z0-9]+'
t_LANG = r'"[^"]*"@[a-zA-Z]+'
t_A = r'a'
t_DOT = r'\.'
t_RBRACKET = r'\{'
t_LBRACKET = r'\}'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

data = '''
# DBPedia: obras de Chuck Berry

select ?nome ?desc where {
    ?s a dbo:MusicalArtist.
    ?s foaf:name "Chuck Berry"@en .
    ?w dbo:artist ?s.
    ?w foaf:name ?nome.
    ?w dbo:abstract ?desc
} LIMIT 1000 # Limite de 1000 resultados
'''

lexer.input(data)

for tok in lexer:
    print(tok)