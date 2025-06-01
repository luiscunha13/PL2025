import ply.yacc as yacc
from analex import tokens, lexer

# Precedencia e associatividade dos operadores
precedence = (
    ('right', 'IF'),
    ('right', 'ELSE', 'THEN'),
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQUAL', 'NOTEQUAL', 'LESS', 'GREATER', 'LESSEQUAL', 'GREATEREQUAL'),
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIVIDE', 'DIV', 'MOD', 'POW'),
    ('right', 'UMINUS'),
    ('left', 'AT')
)


def p_program(p):
    '''program : PROGRAM ID SEMICOLON block DOT'''
    p[0] = ('program', p[2], p[4])


def p_block(p):
    '''block : optional_declarations compound_statement'''
    p[0] = ('block', p[1], p[2])


def p_optional_declarations(p):
    '''optional_declarations : declarations
                            | empty'''
    p[0] = p[1]


def p_declarations(p):
    '''declarations : declaration_section
                   | declarations declaration_section'''
    if len(p) == 2:
        p[0] = ('declarations', [p[1]])
    else:
        p[0] = ('declarations', p[1][1] + [p[2]])


def p_declaration_section(p):
    '''declaration_section : VAR var_declaration_list SEMICOLON
                          | CONST const_declaration_list SEMICOLON
                          | TYPE type_declaration_list SEMICOLON
                          | FUNCTION function_declaration SEMICOLON
                          | PROCEDURE procedure_declaration SEMICOLON'''
    p[0] = (p[1].lower() + '_declarations', p[2])


def p_var_declaration_list(p):
    '''var_declaration_list : var_declaration
                           | var_declaration_list SEMICOLON var_declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_const_declaration_list(p):
    '''const_declaration_list : const_declaration
                             | const_declaration_list SEMICOLON const_declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_type_declaration_list(p):
    '''type_declaration_list : type_declaration
                            | type_declaration_list SEMICOLON type_declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_function_declaration(p):
    '''function_declaration : ID parameters COLON type SEMICOLON block
                           | ID parameters COLON type SEMICOLON FORWARD SEMICOLON'''
    if p[6] == 'forward':
        p[0] = ('function_forward', p[1], p[2], p[4])
    else:
        p[0] = ('function', p[1], p[2], p[4], p[6])


def p_procedure_declaration(p):
    '''procedure_declaration : ID parameters SEMICOLON block
                            | ID parameters SEMICOLON FORWARD SEMICOLON'''
    if len(p) == 5:
        p[0] = ('procedure_forward', p[1], p[2])
    else:
        p[0] = ('procedure', p[1], p[2], p[4])


def p_parameters(p):
    '''parameters : LPAREN parameter_list RPAREN
                 | empty'''
    p[0] = [] if len(p) == 2 else p[2]


def p_parameter_list(p):
    '''parameter_list : parameter
                     | parameter_list SEMICOLON parameter'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_parameter(p):
    '''parameter : ID_list COLON type
                 | VAR ID_list COLON type'''
    if len(p) == 4:
        p[0] = ('val_param', p[1], p[3])
    else:
        p[0] = ('var_param', p[2], p[4])


def p_var_declaration(p):
    '''var_declaration : ID_list COLON type'''
    p[0] = ('var_declaration', p[1], p[3])


def p_const_declaration(p):
    '''const_declaration : ID EQUAL expression'''
    p[0] = ('const_declaration', p[1], p[3])


def p_type_declaration(p):
    '''type_declaration : ID EQUAL type'''
    p[0] = ('type_declaration', p[1], p[3])


def p_ID_list(p):
    '''ID_list : ID
               | ID_list COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_type(p):
    '''type : INTEGER
            | REAL
            | BOOLEAN
            | CHAR
            | STRING
            | SET OF type
            | FILE OF type
            | ARRAY LBRACKET INTEGER_CONST RANGE INTEGER_CONST RBRACKET OF type
            | RECORD field_list END
            | ID'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] == 'array':
        p[0] = ('array', (p[3], p[5]), p[8])
    elif p[1] == 'set':
        p[0] = ('set', p[3])
    elif p[1] == 'file':
        p[0] = ('file', p[3])
    else:
        p[0] = ('record', p[2])


def p_field_list(p):
    '''field_list : var_declaration SEMICOLON
                 | field_list var_declaration SEMICOLON'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_compound_statement(p):
    '''compound_statement : BEGIN statement_list END'''
    p[0] = ('compound_statement', p[2])


def p_statement_list(p):
    '''statement_list : statement
                     | statement_list SEMICOLON statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_statement(p):
    '''statement : non_if_statement
                | if_statement'''
    p[0] = p[1]


def p_non_if_statement(p):
    '''non_if_statement : assignment_statement
                       | while_statement
                       | for_statement
                       | compound_statement
                       | writeln_statement
                       | readln_statement
                       | function_call_statement
                       | BREAK
                       | CONTINUE
                       | EXIT
                       | RETURN expression
                       | empty'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('return', p[2])


def p_if_statement(p):
    '''if_statement : IF expression THEN statement %prec THEN
                   | IF expression THEN statement ELSE statement'''
    if len(p) == 5:
        p[0] = ('if', p[2], p[4])
    else:
        p[0] = ('if-else', p[2], p[4], p[6])


def p_assignment_statement(p):
    '''assignment_statement : variable ASSIGN expression'''
    p[0] = ('assign', p[1], p[3])


def p_while_statement(p):
    '''while_statement : WHILE expression DO statement'''
    p[0] = ('while', p[2], p[4])


def p_for_statement(p):
    '''for_statement : FOR ID ASSIGN expression TO expression DO statement
                    | FOR ID ASSIGN expression DOWNTO expression DO statement'''
    p[0] = ('for', p[2], p[4], p[5], p[6], p[8])


def p_writeln_statement(p):
    '''writeln_statement : WRITELN LPAREN expression_list RPAREN
                        | WRITELN LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = ('writeln', p[3])
    else:
        p[0] = ('writeln', [])


def p_readln_statement(p):
    '''readln_statement : READLN LPAREN variable_list RPAREN
                       | READLN LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = ('readln', p[3])
    else:
        p[0] = ('readln', [])

def p_function_call_statement(p):
    '''function_call_statement : ID LPAREN argument_list RPAREN
                              | ID LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = ('function_call', p[1], p[3])
    else:
        p[0] = ('function_call', p[1], [])


def p_expression_list(p):
    '''expression_list : expression
                      | expression_list COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_variable_list(p):
    '''variable_list : variable
                    | variable_list COMMA variable'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_variable(p):
    '''variable : ID
               | ID LBRACKET expression RBRACKET
               | AT ID
               | ID LPAREN argument_list RPAREN
               | ID LPAREN RPAREN'''
    if len(p) == 2:
        p[0] = ('var', p[1])
    elif p[1] == '@':
        p[0] = ('pointer', p[2])
    elif p[2] == '[':
        p[0] = ('array_access', p[1], p[3])
    elif len(p) == 4:
        p[0] = ('function_call', p[1], [])
    else:
        p[0] = ('function_call', p[1], p[3])


def p_argument_list(p):
    '''argument_list : expression
                    | argument_list COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]]


def p_expression(p):
    '''expression : simple_expression
                 | simple_expression relational_operator simple_expression'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('binary_op', p[2], p[1], p[3])


def p_simple_expression(p):
    '''simple_expression : term
                        | ADD term %prec UMINUS
                        | SUB term %prec UMINUS
                        | simple_expression adding_operator term'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ('unary_op', p[1], p[2])
    else:
        p[0] = ('binary_op', p[2], p[1], p[3])


def p_term(p):
    '''term : factor
            | term multiplying_operator factor
            | term POW factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('binary_op', p[2], p[1], p[3])


def p_factor(p):
    '''factor : variable
             | INTEGER_CONST
             | REAL_CONST
             | STRING_CONST
             | LPAREN expression RPAREN
             | CHAR_CONST
             | HEX_CONST
             | TRUE
             | FALSE
             | NOT factor'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] == '(':
        p[0] = p[2]
    else:
        p[0] = ('unary_op', p[1], p[2])


def p_relational_operator(p):
    '''relational_operator : EQUAL
                          | NOTEQUAL
                          | LESS
                          | GREATER
                          | LESSEQUAL
                          | GREATEREQUAL'''
    p[0] = p[1]


def p_adding_operator(p):
    '''adding_operator : ADD
                      | SUB
                      | OR'''
    p[0] = p[1]


def p_multiplying_operator(p):
    '''multiplying_operator : MUL
                           | DIVIDE
                           | DIV
                           | MOD
                           | AND'''
    p[0] = p[1]


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    if p:
        print(
            f"Erro sintático na linha {p.lineno}, coluna {find_column(lexer.lexdata, p)}: Token inesperado: '{p.value}'")
    else:
        print("Erro sintático no final do arquivo")


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


parser = yacc.yacc(debug=True, write_tables=True, outputdir='.')

# Função para analisar o código
def parse_code(code):
    return parser.parse(code, lexer=lexer)
