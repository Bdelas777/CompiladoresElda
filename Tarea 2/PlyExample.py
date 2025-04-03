# Ejemplo de Calculadora Simple con PLY en Python

import ply.lex as lex
import ply.yacc as yacc

# ----- Analizador léxico -----

# Lista de nombres de tokens
tokens = (
    'NUMBER',
    'PLUS',0
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
)

# Expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Un token más complejo
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# ----- Analizador sintáctico -----

# Precedencia de operadores (de menor a mayor)
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# Regla de inicio
def p_expression(p):
    '''
    expression : term
               | expression PLUS term
               | expression MINUS term
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]

def p_term(p):
    '''
    term : factor
         | term TIMES factor
         | term DIVIDE factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        # Manejo de división por cero
        if p[3] == 0:
            print("Error: División por cero")
            p[0] = 0
        else:
            p[0] = p[1] / p[3]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}'")
    else:
        print("Error de sintaxis en EOF")

# Construir el parser
parser = yacc.yacc()

# ----- Función para probar -----
def calcular(s):
    result = parser.parse(s)
    return result

# Pruebas
if __name__ == "__main__":
    while True:
        try:
            s = input('calc > ')
            
            if s == 'exit':
                break
            result = calcular(s)
            print(f"Resultado: {result}")
        except EOFError:
            break