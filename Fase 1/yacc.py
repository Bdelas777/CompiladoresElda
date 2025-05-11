



import ply.yacc as yacc
from lex import tokens
from semantic_cube import Type, Operation, get_result_type
from semantic_analyzer import SemanticAnalyzer
from quadruple_generator import QuadrupleGenerator

semantic = SemanticAnalyzer()
quad_gen = QuadrupleGenerator(semantic)

# Add missing function to get operand name from expression nodes
def get_operand_name(expr_node):
    if isinstance(expr_node, tuple):
        if expr_node[0] == 'id':
            return expr_node[1]
        elif expr_node[0] == 'constant':
            return str(expr_node[1])
        elif expr_node[0] == 'string':
            return expr_node[1]
        # If it's an operation or comparison, the result is a temporary variable
        # which should be the last item pushed onto the PilaO stack
        elif expr_node[0] in ['operation', 'comparison', 'unary']:
            if quad_gen.PilaO:
                return quad_gen.PilaO[-1]
    return str(expr_node)

def p_programa(p):
    '''programa : TOKEN_PROGRAM TOKEN_ID TOKEN_SEMICOLON dec_var dec_funcs TOKEN_MAIN body TOKEN_END'''
    semantic.program_start(p[2])
    semantic.declare_main()
    p[0] = ('programa', p[2], p[4], p[5], p[7])
    semantic.end_main()
    semantic.program_end()
    
    # Print the generated quadruples
    quad_gen.print_quads()

def p_programa_error_no_main(p):
    '''programa : TOKEN_PROGRAM TOKEN_ID TOKEN_SEMICOLON dec_var dec_funcs TOKEN_END'''
    semantic.program_start(p[2])
    semantic.add_error("Missing 'main' section in program")
    p[0] = ('programa_error', p[2], p[4], p[5])
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
    semantic.start_var_declaration()
    if p[3] == None:
        p[0] = ('vars', [p[2]])
    else:
        p[0] = ('vars', [p[2]] + p[3])
        
def p_rep_var(p):
    '''rep_var  : variable rep_var
    |  empty'''
    if p[1] == None:
        p[0] = None
    else:
        if p[2] == None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
        
def p_variable(p):
    '''variable : TOKEN_ID mas_ids TOKEN_COLON type TOKEN_SEMICOLON'''
    semantic.add_id_to_temp_list(p[1])
    ids = [p[1]] + (p[2] if p[2] else [])
    for id in ids[1:]:
        semantic.add_id_to_temp_list(id)
    semantic.set_current_type(p[4])
    semantic.add_vars_to_table()
    p[0] = ('variable', ids, p[4])
    
def p_mas_ids(p):
    '''mas_ids : TOKEN_COMMA TOKEN_ID mas_ids
    |  empty'''
    if p[1] == None:
        p[0] = []
    else:
        if p[3] == None:
            p[0] = [p[2]]
        else:
            p[0] = [p[2]] + p[3]
            
def p_type(p):
    '''type : TOKEN_INT
    | TOKEN_FLOAT'''
    if p[1] not in ['int', 'float']:
        print(f"Error: Tipo inválido '{p[1]}', se esperaba 'int' o 'float'")
        semantic.add_error(f"Invalid type: '{p[1]}', expected 'int' or 'float'")
        p[0] = 'int'  
    else:
        p[0] = p[1]
        
def p_body(p):
    '''body : TOKEN_LBRACE dec_statements TOKEN_RBRACE'''
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
    for expr in p[3]:
        if isinstance(expr, tuple) and expr[0] == 'string':
            quad_gen.generate_print_quad(expr[1])
        else:
            # Get the operand name for non-string expressions
            operand = get_operand_name(expr)
            quad_gen.generate_print_quad(operand)
    p[0] = ('print', p[3])
    
def p_expresiones(p):
    '''expresiones : TOKEN_CTE_STRING comas
    | expresion comas'''
    # Correct handling of string literals
    if p.slice[1].type == 'TOKEN_CTE_STRING':
        p[0] = [('string', p[1])] + (p[2] if p[2] else [])
    else:
        p[0] = [p[1]] + (p[2] if p[2] else [])
        
def p_comas(p):
    '''comas : TOKEN_COMMA expresion comas
    | TOKEN_COMMA TOKEN_CTE_STRING comas
    | empty'''
    if p[1] == None:
        p[0] = []
    elif p.slice[2].type == 'TOKEN_CTE_STRING':
        value = p[2]
        p[0] = [('string', value)] + (p[3] if p[3] else [])
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])
        
def p_cycle(p):
    '''cycle : TOKEN_WHILE TOKEN_LPAREN expresion TOKEN_RPAREN TOKEN_DO body TOKEN_SEMICOLON'''
    # Store the position to return after condition evaluation
    return_position = len(quad_gen.Quads)
    
    expr_type = get_expr_type(p[3])
    semantic.check_condition(expr_type)
    
    # Get the last expression result
    condition = get_operand_name(p[3])
    
    # Generate gotof
    gotof_index = quad_gen.generate_gotof_quad(condition)
    
    # Process the body
    # Body statements are already processed by their respective rules
    
    # Generate goto back to condition
    quad_gen.generate_goto_quad()
    quad_gen.fill_quad(len(quad_gen.Quads) - 1, return_position)
    
    # Fill the gotof with the exit position
    quad_gen.fill_quad(gotof_index, len(quad_gen.Quads))
    
    p[0] = ('while', p[3], p[6])
    
def p_condition(p):
    '''condition : TOKEN_IF TOKEN_LPAREN expresion TOKEN_RPAREN body else TOKEN_SEMICOLON'''
    expr_type = get_expr_type(p[3])
    semantic.check_condition(expr_type)
    
    # Get the last expression result
    condition = get_operand_name(p[3])
    
    # Generate gotof
    gotof_index = quad_gen.generate_gotof_quad(condition)
    
    # Process the body
    # Body statements are already processed by their respective rules
    
    if p[6]:  # If there's an else
        # Generate goto to skip else
        goto_index = quad_gen.generate_goto_quad()
        
        # Fill the gotof with the position after the if body
        quad_gen.fill_quad(gotof_index, len(quad_gen.Quads))
        
        # Process the else body
        # Else body statements are already processed by their respective rules
        
        # Fill the goto with the position after the else body
        quad_gen.fill_quad(goto_index, len(quad_gen.Quads))
    else:
        # Fill the gotof with the position after the if body
        quad_gen.fill_quad(gotof_index, len(quad_gen.Quads))
        
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
    # Determine the type based on the token type
    if p.slice[1].type == 'TOKEN_CTE_INT':
        p[0] = ('constant', p[1], Type.INT)
    else:  # TOKEN_CTE_FLOAT
        p[0] = ('constant', p[1], Type.FLOAT)
    
def p_expresion(p):
    '''expresion : exp comparar'''
    if p[2] == None:
        p[0] = p[1]
    else:
        left_type = get_expr_type(p[1])
        right_type = get_expr_type(p[2][1])
        op = token_to_operation(p[2][0])
        result_type = semantic.check_expression_compatibility(left_type, right_type, op)
        
        # Add the left operand to stacks
        left_operand = get_operand_name(p[1])
        quad_gen.process_operand(left_operand, left_type)
        
        # Add the comparison operator
        quad_gen.process_operator(p[2][0])
        
        # Add the right operand to stacks
        right_operand = get_operand_name(p[2][1])
        quad_gen.process_operand(right_operand, right_type)
        
        # Generate the quadruple
        quad_gen.generate_arithmetic_quad()
        
        # Create and return the comparison node
        p[0] = ('comparison', p[1], p[2][0], p[2][1])
        p[0] = set_expr_type(p[0], result_type)
        
def p_comparar(p):
    '''comparar  : signo exp
    | empty'''
    if p[1] == None:
        p[0] = None
    else:
        p[0] = (p[1], p[2])
        
def p_signo(p):
    '''signo : TOKEN_GT
    | TOKEN_LT
    | TOKEN_NE'''
    p[0] = p[1]
    
def p_exp(p):
    '''exp  : termino suma_resta'''
    if p[2] == None:
        p[0] = p[1]
    else:
        left_type = get_expr_type(p[1])
        right_type = get_expr_type(p[2][1])
        op = token_to_operation(p[2][0])
        result_type = semantic.check_expression_compatibility(left_type, right_type, op)
        
        # Add the left operand to stacks
        left_operand = get_operand_name(p[1])
        quad_gen.process_operand(left_operand, left_type)
        
        # Add the operator
        quad_gen.process_operator(p[2][0])
        
        # Add the right operand to stacks
        right_operand = get_operand_name(p[2][1])
        quad_gen.process_operand(right_operand, right_type)
        
        # Generate the quadruple
        quad_gen.generate_arithmetic_quad()
        
        # Create and return the operation node
        p[0] = ('operation', p[1], p[2][0], p[2][1])
        p[0] = set_expr_type(p[0], result_type)
        
def p_suma_resta(p):
    '''suma_resta : TOKEN_PLUS termino suma_resta
    | TOKEN_MINUS termino suma_resta
    | empty'''
    if p[1] == None:
        p[0] = None
    else:
        if p[3] == None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ('operation', p[2], p[3][0], p[3][1]) if isinstance(p[3], tuple) and len(p[3]) > 1 else p[2])
            
def p_termino(p):
    '''termino : factor multi_div'''
    if p[2] == None:
        p[0] = p[1]
    else:
        left_type = get_expr_type(p[1])
        right_type = get_expr_type(p[2][1])
        op = token_to_operation(p[2][0])
        result_type = semantic.check_expression_compatibility(left_type, right_type, op)
        
        # Add the left operand to stacks
        left_operand = get_operand_name(p[1])
        quad_gen.process_operand(left_operand, left_type)
        
        # Add the operator
        quad_gen.process_operator(p[2][0])
        
        # Add the right operand to stacks
        right_operand = get_operand_name(p[2][1])
        quad_gen.process_operand(right_operand, right_type)
        
        # Generate the quadruple
        quad_gen.generate_arithmetic_quad()
        
        # Create and return the operation node
        p[0] = ('operation', p[1], p[2][0], p[2][1])
        p[0] = set_expr_type(p[0], result_type)
        
def p_multi_div(p):
    '''multi_div  : operacion_mul_div factor multi_div  
    | empty'''
    if p[1] == None:
        p[0] = None
    else:
        if p[3] == None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ('operation', p[2], p[3][0], p[3][1]) if isinstance(p[3], tuple) and len(p[3]) > 1 else p[2])
            
def p_operacion_mul_div(p):
    '''operacion_mul_div : TOKEN_DIV
    | TOKEN_MULT'''
    p[0] = p[1]
    
def p_factor(p):
    '''factor : definicion
    | operaciones'''
    p[0] = p[1]
    
def p_definicion(p):
    '''definicion : TOKEN_LPAREN expresion TOKEN_RPAREN'''
    # Add false bottom before processing the expression
    quad_gen.push_false_bottom()
    
    # Expression processing handled by expresion rule
    
    # Remove false bottom after processing
    quad_gen.pop_false_bottom()
    
    p[0] = p[2]
    
def p_operaciones(p):
    '''operaciones : opciones_mas_menos id_cte'''
    if p[1] == None:
        p[0] = p[2]
    else:
        expr_type = get_expr_type(p[2])
        if expr_type not in [Type.INT, Type.FLOAT]:
            semantic.add_error(f"Unary operation not supported for type {expr_type}")
        
        # For unary operations, we'll use a special approach
        operand = get_operand_name(p[2])
        
        if p[1] == '-':
            # For negative, generate a quadruple that multiplies by -1
            quad_gen.process_operand("-1", Type.INT)  # push -1
            quad_gen.process_operand(operand, expr_type)  # push the operand
            quad_gen.process_operator('*')  # push multiply operator
            quad_gen.generate_arithmetic_quad()  # generate the quadruple
            
        p[0] = ('unary', p[1], p[2])
        p[0] = set_expr_type(p[0], expr_type)
        
def p_opciones_mas_menos(p):
    '''opciones_mas_menos : TOKEN_PLUS
    | TOKEN_MINUS
    | empty'''
    p[0] = p[1]
    
def p_id_cte(p):
    '''id_cte : TOKEN_ID
    | cte'''
    if isinstance(p[1], tuple):
        p[0] = p[1]
    else:
        if p[1] and p.slice[1].type == 'TOKEN_ID':
            var_type = semantic.check_variable(p[1])
            p[0] = ('id', p[1])
            p[0] = set_expr_type(p[0], var_type)
        else:
            if p.slice[1].type == 'cte':
                p[0] = p[1]
            else:
                p[0] = ('id', p[1])
                
def p_funcs(p):
    '''funcs :  TOKEN_VOID TOKEN_ID scopefun TOKEN_LPAREN tipo TOKEN_RPAREN TOKEN_LCOL var body TOKEN_RCOL TOKEN_SEMICOLON'''
    func = semantic.check_function(p[2])    
    params = p[5] if p[5] else []
    if isinstance(params, list):
        for param in params:
            if isinstance(param, tuple) and len(param) >= 3 and param[0] == 'param':
                param_id = param[1]
                param_type = param[2]                
                if param_type not in ['int', 'float']:
                    semantic.add_error(f"Invalid parameter type '{param_type}' for parameter '{param_id}' in function '{p[2]}'")
                    continue  
                semantic.add_parameter(param_id, param_type)
    p[0] = ('function', p[2], p[5] if p[5] else [], p[8], p[9])
    semantic.end_function_declaration()

def p_scopefun(p):
    '''scopefun : empty'''
    function_name = p[-1]
    semantic.declare_function(function_name)
    print(f"Function scope established: {function_name}")
    return True
    
def p_tipo(p):
    '''tipo : def_tipo
    | empty'''
    p[0] = p[1]
    
def p_def_tipo(p):
    '''def_tipo : TOKEN_ID TOKEN_COLON type coma'''
    if p[4] == None:
        p[0] = [('param', p[1], p[3])]
    else:
        p[0] = [('param', p[1], p[3])] + p[4]
        
def p_coma(p):
    '''coma : TOKEN_COMMA TOKEN_ID TOKEN_COLON type coma
    | empty'''
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
    func = semantic.check_function(p[1])
    if func:
        args = p[3] if p[3] else []
        if len(args) != len(func.parameters):
            semantic.add_error(f"Function '{p[1]}' expects {len(func.parameters)} arguments, got {len(args)}")
        else:
            for i, (arg, param) in enumerate(zip(args, func.parameters)):
                arg_type = get_expr_type(arg)
                param_type = param.type
                result_type = get_result_type(param_type, arg_type, Operation.ASSIGN)
                if result_type == Type.ERROR:
                    semantic.add_error(f"Parameter type mismatch in call to '{p[1]}': Parameter {i+1} expects {param_type}, got {arg_type}")
        
        # Generate function call quadruple
        quad_gen.Quads.append(quad_gen.Quadruple('call', p[1], None, None))
        quad_gen.quad_counter += 1
        
    p[0] = ('function_call', p[1], p[3] if p[3] else [])
    
def p_def_exp(p):
    '''def_exp : expresion coma2
    | empty'''
    if p[1] is None:
        p[0] = []
    else:
        # Generate param quadruple for each argument
        operand = get_operand_name(p[1])
        quad_gen.Quads.append(quad_gen.Quadruple('param', operand, None, None))
        quad_gen.quad_counter += 1
        
        args = [p[1]]
        if p[2]:
            for arg in p[2]:
                operand = get_operand_name(arg)
                quad_gen.Quads.append(quad_gen.Quadruple('param', operand, None, None))
                quad_gen.quad_counter += 1
            args.extend(p[2])
        
        p[0] = args
        
def p_coma2(p):
    '''coma2 : TOKEN_COMMA expresion coma2
    | empty'''
    if p[1] == None:
        p[0] = []
    else:
        p[0] = [p[2]] + (p[3] if p[3] else [])
        
def p_assign(p):
    '''assign : TOKEN_ID TOKEN_ASSIGN expresion TOKEN_SEMICOLON'''
    var_type = semantic.check_variable(p[1])
    expr_type = get_expr_type(p[3])
    semantic.check_assignment_compatibility(p[1], expr_type)
    
    # Get the result of the expression
    expression_result = get_operand_name(p[3])
    
    # Generate assignment quadruple
    quad_gen.generate_assignment_quad(p[1], expression_result)
    
    p[0] = ('assign', p[1], p[3])
    
def p_empty(p):
    'empty :'
    p[0] = None
    
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at EOF")
    
def token_to_operation(token):
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
    if isinstance(expr_node, tuple):
        # Add the type information in a more structured way
        # Check if 'type' is already in the tuple
        for i in range(len(expr_node)):
            if expr_node[i] == 'type':
                # Create a new tuple with updated type
                return expr_node[:i] + ('type', expr_type) + expr_node[i+2:]
        # If 'type' is not already in the tuple, add it
        expr_node = expr_node + ('type', expr_type)
    return expr_node
    
def get_expr_type(expr_node):
    if isinstance(expr_node, tuple):
        # First try to find an explicit 'type' field
        for i in range(len(expr_node) - 1):
            if expr_node[i] == 'type' and i + 1 < len(expr_node):
                return expr_node[i + 1]
                
        # If not found, infer based on node type
        if expr_node[0] == 'id':
            return semantic.check_variable(expr_node[1])
        elif expr_node[0] == 'constant':
            # If type is stored in the constant tuple
            if len(expr_node) > 2:
                return expr_node[2]
            # Otherwise infer from value
            elif isinstance(expr_node[1], int):
                return Type.INT
            elif isinstance(expr_node[1], float):
                return Type.FLOAT
            elif isinstance(expr_node[1], str):
                try:
                    float(expr_node[1])
                    if '.' in expr_node[1]:
                        return Type.FLOAT
                    else:
                        return Type.INT
                except:
                    return Type.STRING
        elif expr_node[0] == 'operation':
            left_type = get_expr_type(expr_node[1])
            right_type = get_expr_type(expr_node[3])
            op = token_to_operation(expr_node[2])
            return get_result_type(left_type, right_type, op)
        elif expr_node[0] == 'comparison':
            return Type.BOOL
        elif expr_node[0] == 'function_call_expr':
            func = semantic.check_function(expr_node[1])
            if func:
                return func.return_type
        elif expr_node[0] == 'string':
            return Type.STRING
    return Type.ERROR
    
parser = yacc.yacc(debug=False)

def parse_program(code):
    global semantic
    semantic = SemanticAnalyzer()
    global quad_gen
    quad_gen = QuadrupleGenerator(semantic)
    result = parser.parse(code)
    return result, semantic.error_list
    
if __name__ == "__main__":
    data = '''
program test1;
var
e, z : int;
    x, y, a : float;
void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];
main{
    a = 1 + 2;
}
end
    '''
    result = parser.parse(data)
    
    # Test additional case without main
    data_without_main = '''
program sinmain;
var a : int;
void saluda()
[
    {
        a = 3;
    }
];
end
    '''
    result_without_main = parser.parse(data_without_main)
    semantic.print_function_directory()
