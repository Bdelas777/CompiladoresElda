# babyduck_lexer.py
import ply.lex as lex

# List of token names
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
]

# Reserved words
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
    'end': 'TOKEN_END',
}

# Add reserved words to tokens list
tokens += list(reserved.values())

# Regular expression rules for simple tokens
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

# Regular expression rules with actions
def t_TOKEN_CTE_FLOAT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_TOKEN_CTE_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_TOKEN_CTE_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_TOKEN_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'TOKEN_ID')
    return t

# Define a rule to track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Characters to ignore (whitespace and tabs)
t_ignore = ' \t'

# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# For testing the lexer directly
if __name__ == "__main__":
    # Test input
    data = '''
    program test;
    var x, y: int;
    
    void main() {
        x = 10;
        y = 3.14;
        if (x > 5) {
            print("x is greater than 5");
        };
    } end
    '''
    
    # Give the lexer the input
    lexer.input(data)
    
    # Tokenize
    for tok in lexer:
        print(f"Token: {tok.type}, Value: {tok.value}")