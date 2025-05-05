# yacc_integrado.py - Parser for BabyDuck language with semantic analysis
import ply.yacc as yacc
from lex import tokens
from semantic_cube import Type, Operation, get_result_type
from semantic_analyzer import SemanticAnalyzer

# Inicializar analizador semántico
semantic = SemanticAnalyzer()

def p_programa(p):
    '''programa : TOKEN_PROGRAM TOKEN_ID TOKEN_SEMICOLON dec_var dec_funcs TOKEN_MAIN body TOKEN_END'''
    # Punto P1, P2: Inicializar programa
    semantic.program_start(p[2])
    # Add this line to declare main function
    semantic.declare_main()
    p[0] = ('programa', p[2], p[4], p[5], p[7])
    # Punto P5: Finalizar programa
    semantic.end_main()  
    semantic.program_end()

def p_dec_var(p):
    '''dec_var : vars 
         | empty'''
    p[0] = p[1]

def p_dec_funcs(p):
    '''dec_funcs : funcs dec_funcs
                | empty'''
    if p[1] == None:
        p[0] = []
    else:
        if isinstance(p[2], list):
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

def p_vars(p):
    '''vars : TOKEN_VAR variable rep_var'''
    # Punto V1: Iniciar declaración de variables
    semantic.start_var_declaration()
    if p[3] == None:
        p[0] = ('vars', [p[2]])
    else:
        p[0] = ('vars', [p[2]] + p[3])

def p_rep_var(p):
    '''rep_var : variable rep_var
        | empty'''
    if p[1] == None:
        p[0] = None
    else:
        if p[2] == None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

def p_variable(p):
    '''variable : TOKEN_ID mas_ids TOKEN_COLON type TOKEN_SEMICOLON'''
    # Punto V2: Añadir identificador a lista temporal
    semantic.add_id_to_temp_list(p[1])
    ids = [p[1]] + (p[2] if p[2] else [])
    for id in ids[1:]:  # El primer ID ya se procesó arriba
        semantic.add_id_to_temp_list(id)
    
    # Punto V4: Establecer tipo para variables
    semantic.set_current_type(p[4])
    
    # Punto V5: Añadir variables a tabla
    semantic.add_vars_to_table()
    
    p[0] = ('variable', ids, p[4])

def p_mas_ids(p):
    '''mas_ids : TOKEN_COMMA TOKEN_ID mas_ids 
        | empty'''
    if p[1] == None:
        p[0] = []
    else:
        # Punto V6: Añadir más identificadores
        semantic.add_id_to_temp_list(p[2])
        p[0] = [p[2]] + (p[3] if p[3] else [])

def p_type(p):
    '''type : TOKEN_INT 
        | TOKEN_FLOAT'''
    # Punto T1: Determinar tipo
    p[0] = p[1]

def p_body(p):
    '''body : TOKEN_LBRACE dec_statements TOKEN_RBRACE'''
    # Punto B1 y B2: Manejo de bloques
    p[0] = ('body', p[2] if p[2] else [])

def p_dec_statements(p):
    '''dec_statements : statement dec_statements 
        | empty'''
    if p[1] == None:
        p[0] = []
    else:
        if isinstance(p[2], list):
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

def p_statement(p):
    '''statement : assign 
        | condition 
        | cycle 
        | f_call 
        | print'''
    p[0] = p[1]

def p_print(p):
    '''print : TOKEN_PRINT TOKEN_LPAREN expresiones TOKEN_RPAREN TOKEN_SEMICOLON'''
    # Punto PR1, PR2, PR3: Manejo de impresión
    p[0] = ('print', p[3])

def p_expresiones(p):
    '''expresiones : TOKEN_CTE_STRING comas 
        | expresion comas'''
    if isinstance(p[1], str):  # TOKEN_CTE_STRING
        # Punto EX1: Registrar cadena constante
        p[0] = [('string', p[1])] + (p[2] if p[2] else [])
    else:
        # Punto EX2: Evaluar expresión
        p[0] = [p[1]] + (p[2] if p[2] else [])

def p_comas(p):
    '''comas : TOKEN_COMMA expresion comas 
        | TOKEN_COMMA TOKEN_CTE_STRING comas 
        | empty'''
    # Punto CM2: Preparar siguiente elemento
    if p[1] == None:
        p[0] = []
    elif p[2] == 'TOKEN_CTE_STRING' or isinstance(p[2], str):
        value = p[2] if isinstance(p[2], str) else 'unknown'
        p[0] = [('string', value)] + (p[3] if p[3] else [])
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])

def p_cycle(p):
    '''cycle : TOKEN_WHILE TOKEN_LPAREN expresion TOKEN_RPAREN TOKEN_DO body TOKEN_SEMICOLON'''
    # Punto CY1, CY2, CY3, CY4: Manejo de ciclos while
    expr_type = get_expr_type(p[3])
    semantic.check_condition(expr_type)
    p[0] = ('while', p[3], p[6])

def p_condition(p):
    '''condition : TOKEN_IF TOKEN_LPAREN expresion TOKEN_RPAREN body else TOKEN_SEMICOLON'''
    # Punto CO1, CO2, CO3, CO4, CO5: Manejo de condiciones if-else
    expr_type = get_expr_type(p[3])
    semantic.check_condition(expr_type)
    p[0] = ('if', p[3], p[5], p[6])

def p_else(p):
    '''else : TOKEN_ELSE body 
        | empty'''
    if p[1] == None:
        p[0] = None
    else:
        p[0] = p[2]

def p_cte(p):
    '''cte : TOKEN_CTE_INT 
        | TOKEN_CTE_FLOAT'''
    # Punto CT1: Determinar tipo de constante
    p[0] = ('constant', p[1])

def p_expresion(p):
    '''expresion : exp comparar'''
    # Punto E1, E2: Evaluar expresión
    if p[2] == None:
        p[0] = p[1]
    else:
        # Verificar compatibilidad de tipos
        left_type = get_expr_type(p[1])
        right_type = get_expr_type(p[2][1])
        op = token_to_operation(p[2][0])
        result_type = semantic.check_expression_compatibility(left_type, right_type, op)
        
        p[0] = ('comparison', p[1], p[2][0], p[2][1])
        p[0] = set_expr_type(p[0], result_type)

def p_comparar(p):
    '''comparar : signo exp 
        | empty'''
    # Punto CP1, CP2: Manejo de comparaciones
    if p[1] == None:
        p[0] = None
    else:
        p[0] = (p[1], p[2])

def p_signo(p):
    '''signo : TOKEN_GT 
        | TOKEN_LT 
        | TOKEN_NE'''
    # Punto SG1: Guardar operador de comparación
    p[0] = p[1]

def p_exp(p):
    '''exp : termino suma_resta'''
    # Punto EP1, EP2: Evaluar expresión aritmética
    if p[2] == None:
        p[0] = p[1]
    else:
        # Verificar compatibilidad de tipos
        left_type = get_expr_type(p[1])
        right_type = get_expr_type(p[2][1])
        op = token_to_operation(p[2][0])
        result_type = semantic.check_expression_compatibility(left_type, right_type, op)
        
        p[0] = ('operation', p[1], p[2][0], p[2][1])
        p[0] = set_expr_type(p[0], result_type)

def p_suma_resta(p):
    '''suma_resta : TOKEN_PLUS termino suma_resta
        | TOKEN_MINUS termino suma_resta 
        | empty'''
    # Punto SR1, SR2: Manejo de sumas y restas
    if p[1] == None:
        p[0] = None
    else:
        if p[3] == None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ('operation', p[2], p[3][0], p[3][1]) if isinstance(p[3], tuple) and len(p[3]) > 1 else p[2])


def p_termino(p):
    '''termino : factor multi_div'''
    # Punto TM1, TM2: Evaluar término
    if p[2] == None:
        p[0] = p[1]
    else:
        # Verificar compatibilidad de tipos
        left_type = get_expr_type(p[1])
        right_type = get_expr_type(p[2][1])
        op = token_to_operation(p[2][0])
        result_type = semantic.check_expression_compatibility(left_type, right_type, op)
        
        p[0] = ('operation', p[1], p[2][0], p[2][1])
        p[0] = set_expr_type(p[0], result_type)

def p_multi_div(p):
    '''multi_div : operacion_mul_div factor termino 
        | empty'''
    # Punto MD1, MD2: Manejo de multiplicaciones y divisiones
    if p[1] == None:
        p[0] = None
    else:
        if p[3] == None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ('operation', p[2], p[3][0], p[3][1]))

def p_operacion_mul_div(p):
    '''operacion_mul_div : TOKEN_DIV 
        | TOKEN_MULT'''
    # Punto OP1: Determinar operador
    p[0] = p[1]

def p_factor(p):
    '''factor : definicion 
        | operaciones'''
    p[0] = p[1]

def p_definicion(p):
    '''definicion : TOKEN_LPAREN expresion TOKEN_RPAREN'''
    # Punto DF1, DF2: Evaluar expresión entre paréntesis
    p[0] = p[2]

def p_operaciones(p):
    '''operaciones : opciones_mas_menos id_cte'''
    # Punto OP2, OP3: Manejo de operaciones unarias
    if p[1] == None:
        p[0] = p[2]
    else:
        # Si es un operador unario, verificar tipo
        expr_type = get_expr_type(p[2])
        if expr_type not in [Type.INT, Type.FLOAT]:
            semantic.add_error(f"Unary operation not supported for type {expr_type}")
        
        p[0] = ('unary', p[1], p[2])
        p[0] = set_expr_type(p[0], expr_type)  # Mismo tipo que el operando

def p_opciones_mas_menos(p):
    '''opciones_mas_menos : TOKEN_PLUS
        | TOKEN_MINUS 
        | empty'''
    # Punto OPC1: Determinar signo unario
    p[0] = p[1]

def p_id_cte(p):
    '''id_cte : TOKEN_ID
              | cte'''
    # Punto IC1, IC2: Verificar variables e identificadores
    if isinstance(p[1], tuple):
        p[0] = p[1]
    else:
        if p[1] and p.slice[1].type == 'TOKEN_ID':
            # Verificar que la variable exista
            var_type = semantic.check_variable(p[1])
            p[0] = ('id', p[1])
            p[0] = set_expr_type(p[0], var_type)
        else:
            # Es una constante
            if p.slice[1].type == 'cte':
                p[0] = p[1]  # Propagar tipo de constante
            else:
                p[0] = ('id', p[1])

def p_funcs(p):
    '''funcs : TOKEN_VOID TOKEN_ID TOKEN_LPAREN tipo TOKEN_RPAREN TOKEN_LCOL var body TOKEN_RCOL TOKEN_SEMICOLON'''
    # Punto F1, F2: Declaración de función
    semantic.declare_function(p[2])
    # Añadir parámetros
    params = p[4] if p[4] else []
    for param in params:
        if isinstance(param, tuple) and param[0] == 'param':
            param_name, param_type = param[1], param[2]
            semantic.add_parameter(param_name, param_type)
    
    p[0] = ('function', p[2], p[4] if p[4] else [], p[6], p[7])
    
    # Punto F5: Finalizar declaración de función
    semantic.end_function_declaration()

def p_tipo(p):
    '''tipo : def_tipo 
        | empty'''
    p[0] = p[1]

def p_def_tipo(p):
    '''def_tipo : TOKEN_ID TOKEN_COLON type coma'''
    # Punto DT1, DT2: Definición de parámetros
    if p[4] == None:
        p[0] = [('param', p[1], p[3])]
    else:
        p[0] = [('param', p[1], p[3])] + p[4]

def p_coma(p):
    '''coma : TOKEN_COMMA def_tipo coma 
        | empty'''
    # Punto CM1: Manejo de comas en parámetros
    if p[1] == None:
        p[0] = None
    else:
        new_param = ('param', p[2], p[4])
        if p[5] == None:
            p[0] = [new_param]
        else:
            p[0] = [new_param] + p[5]

def p_var(p):
    '''var : vars  
        | empty'''
    p[0] = p[1]

def p_f_call(p):
    '''f_call : TOKEN_ID TOKEN_LPAREN def_exp TOKEN_RPAREN TOKEN_SEMICOLON'''
    # FC1, FC2, FC3: Llamada a función
    func = semantic.check_function(p[1])
    if func:
        # Verificar número y tipo de parámetros
        args = p[3] if p[3] else []
        if len(args) != len(func.parameters):
            semantic.add_error(f"Function '{p[1]}' expects {len(func.parameters)} arguments, got {len(args)}")
        
        # TODO: Verificar tipos de parámetros
    
    p[0] = ('function_call', p[1], p[3] if p[3] else [])

def p_def_exp(p):
    '''def_exp : expresion coma2 
        | empty'''
    # Punto DE1: Definición de expresiones como argumentos
    if p[1] == None:
        p[0] = []
    else:
        p[0] = [p[1]] + (p[2] if p[2] else [])

def p_coma2(p):
    '''coma2 : TOKEN_COMMA expresion coma2 
        | empty'''
    # Punto CM3: Manejo de comas en argumentos
    if p[1] == None:
        p[0] = []
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])

def p_assign(p):
    '''assign : TOKEN_ID TOKEN_ASSIGN expresion TOKEN_SEMICOLON'''
    # Punto A1, A2, A3: Asignación de variables
    var_type = semantic.check_variable(p[1])
    expr_type = get_expr_type(p[3])
    semantic.check_assignment_compatibility(p[1], expr_type)
    
    p[0] = ('assign', p[1], p[3])

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"ERROR: Syntax error at '{p.value}', line {p.lineno}")
        print(f"ERROR: Token type: {p.type}")
    else:
        print("ERROR: Syntax error at EOF")

# Funciones auxiliares para manejar tipos en expresiones
def token_to_operation(token):
    """Convierte un token de operación a su equivalente en enum Operation"""
    if token == '+' or token == 'TOKEN_PLUS':
        return Operation.PLUS
    elif token == '-' or token == 'TOKEN_MINUS':
        return Operation.MINUS
    elif token == '*' or token == 'TOKEN_MULT':
        return Operation.MULTIPLY
    elif token == '/' or token == 'TOKEN_DIV':
        return Operation.DIVIDE
    elif token == '>' or token == 'TOKEN_GT':
        return Operation.GREATER
    elif token == '<' or token == 'TOKEN_LT':
        return Operation.LESS
    elif token == '!=' or token == 'TOKEN_NE':
        return Operation.NOT_EQUAL
    elif token == '=' or token == 'TOKEN_ASSIGN':
        return Operation.ASSIGN
    else:
        return None

def set_expr_type(expr_node, expr_type):
    """Establece el tipo de una expresión en el nodo del AST"""
    if isinstance(expr_node, tuple):
        expr_node = expr_node + ('type', expr_type)
    return expr_node

def get_expr_type(expr_node):
    """Obtiene el tipo de una expresión desde el nodo del AST"""
    if isinstance(expr_node, tuple):
        # Buscar si ya tiene tipo asignado
        for i in range(len(expr_node) - 1):
            if expr_node[i] == 'type' and i+1 < len(expr_node):
                return expr_node[i+1]
        
        # Si no tiene tipo asignado, hay que inferirlo
        if expr_node[0] == 'id':
            # Es una variable
            return semantic.check_variable(expr_node[1])
        elif expr_node[0] == 'constant':
            # Es una constante
            if isinstance(expr_node[1], int):
                return Type.INT
            elif isinstance(expr_node[1], float):
                return Type.FLOAT
            elif isinstance(expr_node[1], str):
                # Aquí hay que distinguir entre strings y otros tipos de constantes
                try:
                    float(expr_node[1])
                    if '.' in expr_node[1]:
                        return Type.FLOAT
                    else:
                        return Type.INT
                except:
                    return Type.STRING
        elif expr_node[0] == 'operation':
            # Es una operación binaria
            left_type = get_expr_type(expr_node[1])
            right_type = get_expr_type(expr_node[3])
            op = token_to_operation(expr_node[2])
            return get_result_type(left_type, right_type, op)
        elif expr_node[0] == 'comparison':
            # Es una comparación
            return Type.BOOL
        elif expr_node[0] == 'function_call_expr':
            # Es una llamada a función
            func = semantic.check_function(expr_node[1])
            if func:
                return func.return_type
    
    # Por defecto, si no podemos determinar el tipo
    return Type.ERROR

parser = yacc.yacc()

# Función principal para analizar el código
def parse_program(code):
    # Reiniciar el analizador semántico
    global semantic
    semantic = SemanticAnalyzer()
    
    # Parsear el código
    result = parser.parse(code)
    
    # Imprimir tabla de variables y errores
    semantic.print_function_directory()
    
    return result, semantic.error_list

# Hacemos el testing
if __name__ == "__main__":
    data = '''
    program test;
    var x, y: int;

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