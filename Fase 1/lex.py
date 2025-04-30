# lex.py - Scanner/Lexer for BabyDuck language
import ply.lex as lex

# Palabras que estan reservadas
reserved = {
    'program': 'TOKEN_PROGRAM',
    'var': 'TOKEN_VAR',
    'int': 'TOKEN_INT',
    'float': 'TOKEN_FLOAT',
    'if': 'TOKEN_IF',
    'else': 'TOKEN_ELSE',
    'while': 'TOKEN_WHILE',
    'do': 'TOKEN_DO',
    'print': 'TOKEN_PRINT',
    'void': 'TOKEN_VOID',
    'main': 'TOKEN_MAIN',
    'end': 'TOKEN_END'
}

# Lista de los tokens
tokens = [
    'TOKEN_ID',
    'TOKEN_CTE_INT',
    'TOKEN_CTE_FLOAT',
    'TOKEN_CTE_STRING',
    'TOKEN_PLUS',
    'TOKEN_MINUS',
    'TOKEN_MULT',
    'TOKEN_DIV',
    'TOKEN_GT',
    'TOKEN_LT',
    'TOKEN_NE',
    'TOKEN_ASSIGN',
    'TOKEN_SEMICOLON',
    'TOKEN_COMMA',
    'TOKEN_COLON',
    'TOKEN_LPAREN',
    'TOKEN_RPAREN',
    'TOKEN_LBRACE',
    'TOKEN_RBRACE',
    'TOKEN_GE',
    'TOKEN_LE',
    'TOKEN_EQ'
] + list(reserved.values())

# Expresiones regulares simples
t_TOKEN_PLUS = r'\+'
t_TOKEN_MINUS = r'-'
t_TOKEN_MULT = r'\*'
t_TOKEN_DIV = r'/'
t_TOKEN_GT = r'>'
t_TOKEN_LT = r'<'
t_TOKEN_NE = r'!='
t_TOKEN_ASSIGN = r'='
t_TOKEN_SEMICOLON = r';'
t_TOKEN_COMMA = r','
t_TOKEN_COLON = r':'
t_TOKEN_LPAREN = r'\('
t_TOKEN_RPAREN = r'\)'
t_TOKEN_LBRACE = r'\{'
t_TOKEN_RBRACE = r'\}'

# Expresiones regulares para ids
def t_TOKEN_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'TOKEN_ID')
    return t

# Expresines reguares para flontantes
def t_TOKEN_CTE_FLOAT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t
#Expresiones regulares de enteros
def t_TOKEN_CTE_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

# Expresiones regulares para strings
def t_TOKEN_CTE_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  
    return t

# Comentarios que se descartan si vienen para que el token no los lea
def t_COMMENT(t):
    r'\#.*'
    pass  

# Definimos el salto de linea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

# Manejo de errores
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Construimos el lexer
lexer = lex.lex()

# ´probamos el lexer
if __name__ == "__main__":
    data = '''
    program test;
    var x, y: int;
    var z: float;
    
    main {
        x = 5;
        y = 10;
        z = 3.14;
        
        if (x > y) {
            print("x is greater than y");
        } else {
            print("y is greater or equal to x");
        };
        
        while (z > 0.0) do {
            print(z);
        };
    }
    end
    '''
    
    lexer.input(data)
    
    # Tokenizamos
    for tok in lexer:
        print(tok)