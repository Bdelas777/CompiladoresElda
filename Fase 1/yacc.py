# yacc.py - Parser for BabyDuck language
import ply.yacc as yacc
from lex import tokens

# Program structure
def p_programa(p):
    '''programa : TOKEN_PROGRAM TOKEN_ID TOKEN_SEMICOLON dec_var dec_funs TOKEN_MAIN body TOKEN_END'''
    print(f"DEBUG [programa]: Processing program '{p[2]}'")
    p[0] = ('programa', p[2], p[4], p[5], p[7])
    print(f"DEBUG [programa]: Completed program structure")

def p_dec_var(p):
    '''dec_var : vars
               | empty'''
    print(f"DEBUG [dec_var]: Processing variable declarations")
    p[0] = p[1]
    print(f"DEBUG [dec_var]: Variable declarations processed: {p[0]}")

def p_dec_funs(p):
    '''dec_funs : funs dec_funs
                | empty'''
    print(f"DEBUG [dec_funs]: Processing function declarations")
    if p[1] == None:
        p[0] = []
    else:
        if isinstance(p[2], list):
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    print(f"DEBUG [dec_funs]: Function count: {len(p[0]) if p[0] else 0}")

# Variables declaration
def p_vars(p):
    '''vars : TOKEN_VAR variable rep_var'''
    print(f"DEBUG [vars]: Processing variable block")
    if p[3] == None:
        p[0] = ('vars', [p[2]])
    else:
        p[0] = ('vars', [p[2]] + p[3])
    print(f"DEBUG [vars]: Variables processed: {p[0]}")

def p_rep_var(p):
    '''rep_var : variable rep_var
               | empty'''
    print(f"DEBUG [rep_var]: Processing repeated variables")
    if p[1] == None:
        p[0] = None
        print(f"DEBUG [rep_var]: No more variables")
    else:
        if p[2] == None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
        print(f"DEBUG [rep_var]: Additional variables found: {len(p[0]) if p[0] else 0}")

def p_variable(p):
    '''variable : TOKEN_ID mas_ids TOKEN_COLON type TOKEN_SEMICOLON'''
    ids = [p[1]] + (p[2] if p[2] else [])
    print(f"DEBUG [variable]: Declaring {len(ids)} variables of type {p[4]}: {ids}")
    p[0] = ('variable', ids, p[4])

def p_mas_ids(p):
    '''mas_ids : TOKEN_COMMA TOKEN_ID mas_ids
               | empty'''
    if p[1] == None:
        p[0] = []
        print(f"DEBUG [mas_ids]: No more IDs")
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])
        print(f"DEBUG [mas_ids]: Additional IDs: {p[0]}")

# Types
def p_type(p):
    '''type : TOKEN_INT 
            | TOKEN_FLOAT'''
    print(f"DEBUG [type]: Type is {p[1]}")
    p[0] = p[1]

# Body
def p_body(p):
    '''body : TOKEN_LBRACE dec_statements TOKEN_RBRACE'''
    print(f"DEBUG [body]: Processing code block with {len(p[2]) if p[2] else 0} statements")
    p[0] = ('body', p[2] if p[2] else [])
    print(f"DEBUG [body]: Code block processed")

def p_dec_statements(p):
    '''dec_statements : statement dec_statements
                      | empty'''
    print(f"DEBUG [dec_statements]: Processing statements")
    if p[1] == None:
        p[0] = []
        print(f"DEBUG [dec_statements]: No statements")
    else:
        if isinstance(p[2], list):
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
        print(f"DEBUG [dec_statements]: Total statements: {len(p[0])}")

# Statements
def p_statement(p):
    '''statement : assign
                 | condition
                 | cycle
                 | f_call
                 | print'''
    stmt_type = p[1][0] if isinstance(p[1], tuple) else "unknown"
    print(f"DEBUG [statement]: Processing statement type: {stmt_type}")
    p[0] = p[1]

# Print statement
def p_print(p):
    '''print : TOKEN_PRINT TOKEN_LPAREN expresiones TOKEN_RPAREN TOKEN_SEMICOLON'''
    print(f"DEBUG [print]: Processing print statement with {len(p[3]) if p[3] else 0} expressions")
    p[0] = ('print', p[3])

def p_expresiones(p):
    '''expresiones : TOKEN_CTE_STRING comas
                   | expresion comas'''
    print(f"DEBUG [expresiones]: Processing expressions")
    if isinstance(p[1], str):  # TOKEN_CTE_STRING
        p[0] = [('string', p[1])] + (p[2] if p[2] else [])
        print(f"DEBUG [expresiones]: String literal found: {p[1]}")
    else:
        p[0] = [p[1]] + (p[2] if p[2] else [])
    print(f"DEBUG [expresiones]: Total expressions: {len(p[0])}")

def p_comas(p):
    '''comas : TOKEN_COMMA expresion comas
             | TOKEN_COMMA TOKEN_CTE_STRING comas
             | empty'''
    print(f"DEBUG [comas]: Processing comma-separated expressions")
    if p[1] == None:
        p[0] = []
        print(f"DEBUG [comas]: No more expressions")
    elif p[2] == 'TOKEN_CTE_STRING' or isinstance(p[2], str):
        value = p[2] if isinstance(p[2], str) else 'unknown'
        p[0] = [('string', value)] + (p[3] if p[3] else [])
        print(f"DEBUG [comas]: String literal in comas")
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])
        print(f"DEBUG [comas]: Additional expressions found")

# Cycle (while)
def p_cycle(p):
    '''cycle : TOKEN_WHILE TOKEN_LPAREN expresion TOKEN_RPAREN TOKEN_DO body TOKEN_SEMICOLON'''
    print(f"DEBUG [cycle]: Processing while loop")
    p[0] = ('while', p[3], p[6])
    print(f"DEBUG [cycle]: While loop processed")

# Conditional (if)
def p_condition(p):
    '''condition : TOKEN_IF TOKEN_LPAREN expresion TOKEN_RPAREN body else TOKEN_SEMICOLON'''
    print(f"DEBUG [condition]: Processing if condition")
    p[0] = ('if', p[3], p[5], p[6])
    has_else = "with else" if p[6] else "without else"
    print(f"DEBUG [condition]: If condition processed {has_else}")

def p_else(p):
    '''else : TOKEN_ELSE body
            | empty'''
    if p[1] == None:
        p[0] = None
        print(f"DEBUG [else]: No else clause")
    else:
        p[0] = p[2]
        print(f"DEBUG [else]: Else clause processed")

# Constants
def p_cte(p):
    '''cte : TOKEN_CTE_INT
           | TOKEN_CTE_FLOAT'''
    print(f"DEBUG [cte]: Constant value: {p[1]}")
    p[0] = ('constant', p[1])

# Expressions
def p_expresion(p):
    '''expresion : exp comparar'''
    print(f"DEBUG [expresion]: Processing expression")
    if p[2] == None:
        p[0] = p[1]
        print(f"DEBUG [expresion]: Simple expression (no comparison)")
    else:
        p[0] = ('comparison', p[1], p[2][0], p[2][1])
        print(f"DEBUG [expresion]: Comparison expression with operator: {p[2][0]}")

def p_comparar(p):
    '''comparar : signo exp
                | empty'''
    print(f"DEBUG [comparar]: Processing comparison")
    if p[1] == None:
        p[0] = None
        print(f"DEBUG [comparar]: No comparison operator")
    else:
        p[0] = (p[1], p[2])
        print(f"DEBUG [comparar]: Comparison operator: {p[1]}")

def p_signo(p):
    '''signo : TOKEN_GT
             | TOKEN_LT
             | TOKEN_NE'''
    print(f"DEBUG [signo]: Comparison operator: {p[1]}")
    p[0] = p[1]

# Exp
def p_exp(p):
    '''exp : termino suma_resta'''
    print(f"DEBUG [exp]: Processing arithmetic expression")
    if p[2] == None:
        p[0] = p[1]
        print(f"DEBUG [exp]: Simple term (no addition/subtraction)")
    else:
        p[0] = ('operation', p[1], p[2][0], p[2][1])
        print(f"DEBUG [exp]: Expression with operator: {p[2][0]}")

def p_suma_resta(p):
    '''suma_resta : opcion_mas_menos termino suma_resta
                  | empty'''
    print(f"DEBUG [suma_resta]: Processing addition/subtraction")
    if p[1] == None:
        p[0] = None
        print(f"DEBUG [suma_resta]: No addition/subtraction")
    else:
        if p[3] == None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ('operation', p[2], p[3][0], p[3][1]))
        print(f"DEBUG [suma_resta]: Operator: {p[1]}")

def p_opcion_mas_menos(p):
    '''opcion_mas_menos : TOKEN_PLUS
                        | TOKEN_MINUS'''
    print(f"DEBUG [opcion_mas_menos]: Operator: {p[1]}")
    p[0] = p[1]

# Term
def p_termino(p):
    '''termino : factor multi_div'''
    print(f"DEBUG [termino]: Processing term")
    if p[2] == None:
        p[0] = p[1]
        print(f"DEBUG [termino]: Simple factor (no multiplication/division)")
    else:
        p[0] = ('operation', p[1], p[2][0], p[2][1])
        print(f"DEBUG [termino]: Term with operator: {p[2][0]}")

def p_multi_div(p):
    '''multi_div : operacion_mul_div factor multi_div
                 | empty'''
    print(f"DEBUG [multi_div]: Processing multiplication/division")
    if p[1] == None:
        p[0] = None
        print(f"DEBUG [multi_div]: No multiplication/division")
    else:
        if p[3] == None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ('operation', p[2], p[3][0], p[3][1]))
        print(f"DEBUG [multi_div]: Operator: {p[1]}")

def p_operacion_mul_div(p):
    '''operacion_mul_div : TOKEN_DIV
                         | TOKEN_MULT'''
    print(f"DEBUG [operacion_mul_div]: Operator: {p[1]}")
    p[0] = p[1]

# Factor
def p_factor(p):
    '''factor : definicion
              | operaciones'''
    print(f"DEBUG [factor]: Processing factor")
    p[0] = p[1]

def p_definicion(p):
    '''definicion : TOKEN_LPAREN expresion TOKEN_RPAREN'''
    print(f"DEBUG [definicion]: Processing parenthesized expression")
    p[0] = p[2]
    print(f"DEBUG [definicion]: Parenthesized expression processed")

def p_operaciones(p):
    '''operaciones : opciones_mas_menos id_cte'''
    print(f"DEBUG [operaciones]: Processing operations")
    if p[1] == None:
        p[0] = p[2]
        print(f"DEBUG [operaciones]: Simple value (no unary operator)")
    else:
        p[0] = ('unary', p[1], p[2])
        print(f"DEBUG [operaciones]: Value with unary operator: {p[1]}")

def p_opciones_mas_menos(p):
    '''opciones_mas_menos : TOKEN_PLUS
                          | TOKEN_MINUS
                          | empty'''
    if p[1] == None:
        print(f"DEBUG [opciones_mas_menos]: No unary operator")
    else:
        print(f"DEBUG [opciones_mas_menos]: Unary operator: {p[1]}")
    p[0] = p[1]

def p_id_cte(p):
    '''id_cte : TOKEN_ID
              | cte
              | f_call_expr'''
    if isinstance(p[1], tuple):  # cte or function call
        print(f"DEBUG [id_cte]: Processing complex value")
        p[0] = p[1]
    else:  # TOKEN_ID
        print(f"DEBUG [id_cte]: Processing identifier: {p[1]}")
        p[0] = ('id', p[1])

def p_f_call_expr(p):
    '''f_call_expr : TOKEN_ID TOKEN_LPAREN def_exp TOKEN_RPAREN'''
    print(f"DEBUG [f_call_expr]: Processing function call expression: {p[1]}")
    p[0] = ('function_call_expr', p[1], p[3] if p[3] else [])
    print(f"DEBUG [f_call_expr]: Function call expression processed")

# Functions
def p_funs(p):
    '''funs : TOKEN_VOID TOKEN_ID TOKEN_LPAREN tipo TOKEN_RPAREN var body TOKEN_SEMICOLON'''
    print(f"DEBUG [funs]: Processing function: {p[2]}")
    p[0] = ('function', p[2], p[4] if p[4] else [], p[6], p[7])
    print(f"DEBUG [funs]: Function {p[2]} processed")

def p_tipo(p):
    '''tipo : def_tipo
            | empty'''
    print(f"DEBUG [tipo]: Processing function parameters")
    p[0] = p[1]
    if p[1]:
        param_count = len(p[1]) if isinstance(p[1], list) else 1
        print(f"DEBUG [tipo]: Function has {param_count} parameters")
    else:
        print(f"DEBUG [tipo]: Function has no parameters")

def p_def_tipo(p):
    '''def_tipo : TOKEN_ID TOKEN_COLON type coma'''
    print(f"DEBUG [def_tipo]: Processing parameter: {p[1]} of type {p[3]}")
    if p[4] == None:
        p[0] = [('param', p[1], p[3])]
    else:
        p[0] = [('param', p[1], p[3])] + p[4]
    print(f"DEBUG [def_tipo]: Total parameters: {len(p[0])}")

def p_coma(p):
    '''coma : TOKEN_COMMA TOKEN_ID TOKEN_COLON type coma
            | empty'''
    print(f"DEBUG [coma]: Processing comma in parameters")
    if p[1] == None:
        p[0] = None
        print(f"DEBUG [coma]: No more parameters")
    else:
        new_param = ('param', p[2], p[4])
        if p[5] == None:
            p[0] = [new_param]
        else:
            p[0] = [new_param] + p[5]
        print(f"DEBUG [coma]: Additional parameters found")

def p_var(p):
    '''var : vars
           | empty'''
    print(f"DEBUG [var]: Processing local variables")
    p[0] = p[1]
    if p[1]:
        print(f"DEBUG [var]: Local variables found")
    else:
        print(f"DEBUG [var]: No local variables")

# Function call
def p_f_call(p):
    '''f_call : TOKEN_ID TOKEN_LPAREN def_exp TOKEN_RPAREN TOKEN_SEMICOLON'''
    print(f"DEBUG [f_call]: Processing function call to: {p[1]}")
    p[0] = ('function_call', p[1], p[3] if p[3] else [])
    print(f"DEBUG [f_call]: Function call processed")

def p_def_exp(p):
    '''def_exp : expresion coma2
               | empty'''
    print(f"DEBUG [def_exp]: Processing function arguments")
    if p[1] == None:
        p[0] = []
        print(f"DEBUG [def_exp]: No arguments")
    else:
        p[0] = [p[1]] + (p[2] if p[2] else [])
        print(f"DEBUG [def_exp]: Total arguments: {len(p[0])}")

def p_coma2(p):
    '''coma2 : TOKEN_COMMA expresion coma2
             | empty'''
    print(f"DEBUG [coma2]: Processing comma in arguments")
    if p[1] == None:
        p[0] = []
        print(f"DEBUG [coma2]: No more arguments")
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])
        print(f"DEBUG [coma2]: Additional arguments found")

# Assignment
def p_assign(p):
    '''assign : TOKEN_ID TOKEN_ASSIGN expresion TOKEN_SEMICOLON'''
    print(f"DEBUG [assign]: Processing assignment to: {p[1]}")
    p[0] = ('assign', p[1], p[3])
    print(f"DEBUG [assign]: Assignment processed")

# Empty production
def p_empty(p):
    'empty :'
    print(f"DEBUG [empty]: Processing empty production")
    p[0] = None

# Error rule
def p_error(p):
    if p:
        print(f"ERROR: Syntax error at '{p.value}', line {p.lineno}")
        print(f"ERROR: Token type: {p.type}")
    else:
        print("ERROR: Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

# For testing
if __name__ == "__main__":
    data = '''
    program test;
    var x, y: int;
    var z: float;

    main {
        x = 5;
        y = x + 3;
        if (x > 0) {
            print("x is positive");
        } else {
            print("x is not positive");
        };
        while (y < 10) do {
            y = y + 1;
            print("Looping", y);
        };
    }
    end
    '''

    print("\nDEBUG [main]: Starting parser on test program\n")
    print("-" * 60)
    print(data)
    print("-" * 60 + "\n")
    
    result = parser.parse(data)
    print("\nDEBUG [main]: Parsing completed")
    print(f"\nRESULT: {result}")