import ply.yacc as yacc
from lex import tokens
from semantic_cube import Type, Operation, get_result_type
from semantic_analyzer import SemanticAnalyzer
from quadruple_generator import QuadrupleGenerator, Quadruple
semantic = SemanticAnalyzer()
quad_gen = QuadrupleGenerator(semantic)

def get_operand_name(expr_node):
    if isinstance(expr_node, tuple):
        if expr_node[0] == 'id':
            result = expr_node[1]
            return result
        elif expr_node[0] == 'constant':
            result = str(expr_node[1])
            return result
        elif expr_node[0] == 'string':
            result = expr_node[1]
            return result
        elif expr_node[0] == 'temp_result':
            result = expr_node[1]
            return result
        elif expr_node[0] == 'function_call_expr':
            if quad_gen.PilaO:
                result = quad_gen.PilaO[-1]
                return result
        elif expr_node[0] in ['operation', 'comparison', 'unary']:
            if quad_gen.PilaO:
                result = quad_gen.PilaO[-1]
                return result
        else:
            raise SyntaxError("error_msg: Invalid expression node type")
    result = str(expr_node)
    return result

def p_programa(p):
    '''programa : TOKEN_PROGRAM TOKEN_ID TOKEN_SEMICOLON saveGo dec_var dec_funcs TOKEN_MAIN fillMain body TOKEN_END'''
    semantic.program_start(p[2])
    p[0] = ('programa', p[2], p[5], p[6], p[9])
    semantic.program_end()
    quad_gen.generate_end_quad()
    quad_gen.print_quads()

def p_saveGo(p):
    '''saveGo : empty'''
    goto_index = quad_gen.generate_goto_quad()
    quad_gen.main_goto_index = goto_index
    p[0] = goto_index

def p_fillMain(p):
    '''fillMain : empty'''
    semantic.declare_main()
    if 'main' in semantic.function_directory:
        semantic.function_directory['main'].start_address = len(quad_gen.Quads)
    else:
        semantic.add_error("'main' function not declared")
    if hasattr(quad_gen, 'main_goto_index'):
        quad_gen.fill_quad(quad_gen.main_goto_index, len(quad_gen.Quads))
    p[0] = None

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
            
def p_type_fun(p):
    '''type_fun : TOKEN_INT
    | TOKEN_FLOAT
    | TOKEN_VOID''' 
    if p[1] not in ['int', 'float', 'void']:
        print(f"Error: Tipo inválido '{p[1]}', se esperaba 'int', 'float' o 'void'")
        semantic.add_error(f"Invalid type: '{p[1]}', expected 'int', 'float' or 'void'")
        p[0] = 'int'  
    else:
        p[0] = p[1]
        
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
        | print
        | for_cycle
        | return_stmt'''  
    p[0] = p[1]

def p_return_stmt(p):
    '''return_stmt : TOKEN_RETURN expresion TOKEN_SEMICOLON'''
    if len(p) == 4: 
        return_value = get_operand_name(p[2])
        return_address = quad_gen.get_operand_address(return_value)
        quad_gen.generate_return_quad(return_address)
        p[0] = ('return', p[2])
   
    
def p_print(p):
    '''print : TOKEN_PRINT TOKEN_LPAREN expresiones TOKEN_RPAREN TOKEN_SEMICOLON'''
    for i, expr in enumerate(p[3]):
        if isinstance(expr, tuple) and expr[0] == 'string':
            quad_gen.generate_print_quad(expr[1])
        else:
            operand = get_operand_name(expr)
            operand_address = quad_gen.get_operand_address(operand)
            quad_gen.generate_print_quad(operand_address)
    p[0] = ('print', p[3])
    
def p_expresiones(p):
    '''expresiones : TOKEN_CTE_STRING comas
    | expresion comas'''
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

def p_saveQuad(p):
    '''saveQuad : empty'''
    p[0] = len(quad_gen.Quads)

def p_GotoF(p):
    '''GotoF : empty'''
    condition = get_operand_name(p[-1]) 
    gotof_index = quad_gen.generate_gotof_quad(condition)
    p[0] = gotof_index
           
def p_cycle(p):
    '''cycle : TOKEN_WHILE TOKEN_LPAREN saveQuad expresion GotoF TOKEN_RPAREN TOKEN_DO body TOKEN_SEMICOLON'''
    return_position = p[3]  
    quad_gen.generate_goto_quad()
    quad_gen.fill_quad(len(quad_gen.Quads) - 1, return_position)
    gotof_index = p[5]
    quad_gen.fill_quad(gotof_index, len(quad_gen.Quads))
    
    p[0] = ('while', p[4], p[8])

def p_saveQuadIF(p):
    '''saveQuadIF : empty'''
    condition = get_operand_name(p[-1])
    gotof_index = quad_gen.generate_gotof_quad(condition)
    p[0] = gotof_index
    
def p_GotoFIF(p):
    '''GotoFIF : empty'''
    goto_index = quad_gen.generate_goto_quad()
    gotof_index = p[-3]
    quad_gen.fill_quad(gotof_index, len(quad_gen.Quads))
    p[0] = goto_index

def p_condition(p):
    '''condition : TOKEN_IF TOKEN_LPAREN expresion saveQuadIF TOKEN_RPAREN body GotoFIF else TOKEN_SEMICOLON'''
    expr_type = get_expr_type(p[3])
    semantic.check_condition(expr_type)
    if p[7] is not None:
        goto_index = p[7]
        quad_gen.fill_quad(goto_index, len(quad_gen.Quads))       
    p[0] = ('if', p[3], p[6], p[8])
 
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
    if p.slice[1].type == 'TOKEN_CTE_INT':
        p[0] = ('constant', p[1], Type.INT)
    else:  
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
        left_operand = get_operand_name(p[1])
        quad_gen.process_operand(left_operand, left_type)     
        quad_gen.process_operator(p[2][0])       
        right_operand = get_operand_name(p[2][1])
        quad_gen.process_operand(right_operand, right_type)       
        quad_gen.generate_arithmetic_quad()
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
    '''exp : termino suma_resta'''
    if p[2] is None:
        p[0] = p[1]
    else:
        result = p[1]
        first_type = get_expr_type(result)
        first_operand = get_operand_name(result)
        quad_gen.process_operand(first_operand, first_type)
        for i, (op, operand) in enumerate(p[2]):
            quad_gen.process_operator(op)
            right_type = get_expr_type(operand)
            right_operand = get_operand_name(operand)
            quad_gen.process_operand(right_operand, right_type)
            quad_gen.generate_arithmetic_quad()
        if hasattr(quad_gen, 'PilaO') and quad_gen.PilaO:
            temp_address = quad_gen.PilaO[-1]
            final_type = quad_gen.PTypes[-1] if quad_gen.PTypes else Type.INT
            result = ('temp_result', temp_address, 'type', final_type)
        else:
            result = ('operation', result, p[2][-1][0], p[2][-1][1])
        p[0] = result

def p_operacion_sum_res(p):
    '''operacion_sum_res : TOKEN_PLUS
    | TOKEN_MINUS'''
    p[0] = p[1]

def p_suma_resta(p):
    '''suma_resta  : operacion_sum_res termino suma_resta
                    | empty'''
    if p[1] is None:
        p[0] = None
    else:
        if p[3] is None:
            p[0] = [(p[1], p[2])]
        else:
            p[0] = [(p[1], p[2])] + p[3]
            
def p_termino(p):
    '''termino : factor multi_div'''  
    if p[2] is None:
        p[0] = p[1]
    else:
        result = p[1]
        first_type = get_expr_type(result)
        first_operand = get_operand_name(result)
        quad_gen.process_operand(first_operand, first_type)
        for i, (op, operand) in enumerate(p[2]):
            quad_gen.process_operator(op)
            right_type = get_expr_type(operand)
            right_operand = get_operand_name(operand)
            quad_gen.process_operand(right_operand, right_type)
            quad_gen.generate_arithmetic_quad()
        if hasattr(quad_gen, 'PilaO') and quad_gen.PilaO:
            temp_address = quad_gen.PilaO[-1]
            final_type = quad_gen.PTypes[-1] if quad_gen.PTypes else Type.INT
            result = ('temp_result', temp_address, 'type', final_type)
        else:
            result = ('operation', result, p[2][-1][0], p[2][-1][1])       
        p[0] = result

def p_multi_div(p):
    '''multi_div : operacion_mul_div factor multi_div
                    | empty'''
    if p[1] is None:
        p[0] = None
    else:
        if p[3] is None:
            p[0] = [(p[1], p[2])]
        else:
            p[0] = [(p[1], p[2])] + p[3]
            
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
    quad_gen.push_false_bottom()
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
        operand = get_operand_name(p[2])
        if p[1] == '-':
            quad_gen.process_operand("-1", Type.INT)  
            quad_gen.process_operand(operand, expr_type) 
            quad_gen.process_operator('*')  
            quad_gen.generate_arithmetic_quad() 
        p[0] = ('unary', p[1], p[2])
        p[0] = set_expr_type(p[0], expr_type)
        
def p_opciones_mas_menos(p):
    '''opciones_mas_menos : TOKEN_PLUS
    | TOKEN_MINUS
    | empty'''
    p[0] = p[1]
    
def p_id_cte(p):
    '''id_cte : TOKEN_ID
    | cte
    | function_call_expr'''  
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
    '''funcs : type_fun TOKEN_ID save_func_start TOKEN_LPAREN tipo TOKEN_RPAREN TOKEN_LCOL var body TOKEN_RCOL end_func TOKEN_SEMICOLON'''
    semantic.check_function(p[2])    
    params = p[5] if p[5] else []   
    p[0] = ('function', p[2], params, p[8], p[9])

def p_save_func_start(p):
    '''save_func_start : empty'''
    function_name = p[-1]  
    return_type_str = p[-2] 
    if return_type_str == 'int':
        return_type = Type.INT
    elif return_type_str == 'float':
        return_type = Type.FLOAT
    else:
        return_type = Type.VOID  
    semantic.declare_function(function_name, return_type)
    quad_gen.save_function_start(function_name)
    p[0] = None

def p_end_func(p):
    '''end_func : empty'''
    quad_gen.generate_endfunc_quad()
    semantic.end_function_declaration()
    p[0] = None
    
def p_tipo(p):
    '''tipo : def_tipo
    | empty'''
    if p[1]:
        for param in p[1]:
            if isinstance(param, tuple) and len(param) >= 3 and param[0] == 'param':
                param_id = param[1]
                param_type = param[2]
                if param_type not in ['int', 'float']:
                    semantic.add_error(f"Invalid parameter type '{param_type}' for parameter '{param_id}' in function")
                    continue
                semantic.add_parameter(param_id, param_type)
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
    '''f_call : TOKEN_ID era_quad TOKEN_LPAREN def_exp TOKEN_RPAREN gosub_quad TOKEN_SEMICOLON'''
    func = semantic.check_function(p[1])
    if func:
        args = p[4] if p[4] else []
        if len(args) != len(func.parameters):
            semantic.add_error(f"Function '{p[1]}' expects {len(func.parameters)} arguments, got {len(args)}")
        else:
            for i, (arg, param) in enumerate(zip(args, func.parameters)):
                arg_type = get_expr_type(arg)
                param_type = param.type
                result_type = get_result_type(param_type, arg_type, Operation.ASSIGN)
                if result_type == Type.ERROR:
                    semantic.add_error(f"No hay coincidencia de tipo parametro en la llamada '{p[1]}': Parametro{i+1} espera {param_type}, obtiene {arg_type}")
        
    p[0] = ('function_call', p[1], p[4] if p[4] else [])

def p_function_call_expr(p):
    '''function_call_expr : TOKEN_ID era_quad TOKEN_LPAREN def_exp TOKEN_RPAREN gosub_quad'''
    func = semantic.check_function(p[1])
    if func:
        args = p[4] if p[4] else []
        if len(args) != len(func.parameters):
            semantic.add_error(f"Funcion '{p[1]}' espera {len(func.parameters)} argumentos, obtiene {len(args)}")
        else:
            for i, (arg, param) in enumerate(zip(args, func.parameters)):
                arg_type = get_expr_type(arg)
                param_type = param.type
                result_type = get_result_type(param_type, arg_type, Operation.ASSIGN)
                if result_type == Type.ERROR:
                    semantic.add_error(f"No hay coincidencia de tipo parametro en la llamada '{p[1]}': Parametro{i+1} espera {param_type}, obtiene {arg_type}")
    p[0] = ('function_call_expr', p[1], p[4] if p[4] else [])
    if func and func.return_type != Type.VOID:
        p[0] = set_expr_type(p[0], func.return_type)
        
def p_era_quad(p):
    '''era_quad : empty'''
    function_name = p[-1]
    quad_gen.generate_era_quad(function_name)
    quad_gen.reset_param_counter()
    p[0] = None

def p_gosub_quad(p):
    '''gosub_quad : empty'''
    function_name = p[-5]
    quad_gen.generate_gosub_quad(function_name)
    p[0] = None

def p_def_exp(p):
    '''def_exp : expresion param_quad coma2
    | empty'''
    if p[1] is None:
        p[0] = []
    else:
        args = [p[1]]
        if p[3]:
            args.extend(p[3])
        p[0] = args

def p_param_quad(p):
    '''param_quad : empty'''
    if len(p) > 1 and p[-1] is not None:
        operand = get_operand_name(p[-1])
        operand_address = quad_gen.get_operand_address(operand)
        param_number = quad_gen.increment_param_counter()
        quad_gen.generate_param_quad(operand_address, param_number)
    p[0] = None
         
def p_coma2(p):
    '''coma2 : TOKEN_COMMA expresion param_quad_coma coma2
    | empty'''
    if p[1] == None:
        p[0] = []
    else:
        p[0] = [p[2]] + (p[4] if p[4] else [])

def p_param_quad_coma(p):
    '''param_quad_coma : empty'''
    if len(p) > 1 and p[-1] is not None:
        operand = get_operand_name(p[-1])
        operand_address = quad_gen.get_operand_address(operand)
        param_number = quad_gen.increment_param_counter()
        quad_gen.generate_param_quad(operand_address, param_number)
    p[0] = None
        
def p_assign(p):
    '''assign : TOKEN_ID TOKEN_ASSIGN expresion TOKEN_SEMICOLON'''
    var_type = semantic.check_variable(p[1])
    expr_type = get_expr_type(p[3])
    semantic.check_assignment_compatibility(p[1], expr_type)
    expression_result = get_operand_name(p[3])
    quad_gen.generate_assignment_quad(p[1], expression_result)  
    p[0] = ('assign', p[1], p[3])

def p_for_cycle(p):
    '''for_cycle : TOKEN_FOR TOKEN_LPAREN for_init TOKEN_SEMICOLON saveQuadFor expresion GotoFFor TOKEN_SEMICOLON for_increment TOKEN_RPAREN TOKEN_DO body TOKEN_SEMICOLON'''
    if p[9]:  
        if p[9][0] == 'assign':
            var_name = p[9][1] 
            expr_result = get_operand_name(p[9][2])
            quad_gen.generate_assignment_quad(var_name, expr_result) 
    loop_start = p[5]
    quad_gen.generate_goto_quad()
    quad_gen.fill_quad(len(quad_gen.Quads) - 1, loop_start)
    gotof_index = p[7]  
    quad_gen.fill_quad(gotof_index, len(quad_gen.Quads))
    
    p[0] = ('for', p[3], p[6], p[9], p[12])

def p_for_init(p):
    '''for_init : assign_for
                | empty'''
    p[0] = p[1]

def p_assign_for(p):
    '''assign_for : TOKEN_ID TOKEN_ASSIGN expresion'''
    var_type = semantic.check_variable(p[1])
    expr_type = get_expr_type(p[3])
    semantic.check_assignment_compatibility(p[1], expr_type)
    expression_result = get_operand_name(p[3])
    quad_gen.generate_assignment_quad(p[1], expression_result)  
    p[0] = ('assign', p[1], p[3])

def p_for_increment(p):
    '''for_increment : assign_for_increment
                     | empty'''
    p[0] = p[1]

def p_assign_for_increment(p):
    '''assign_for_increment : TOKEN_ID TOKEN_ASSIGN expresion'''
    var_type = semantic.check_variable(p[1])
    expr_type = get_expr_type(p[3])
    semantic.check_assignment_compatibility(p[1], expr_type)
    expression_result = get_operand_name(p[3])
    p[0] = ('assign', p[1], p[3])

def p_saveQuadFor(p):
    '''saveQuadFor : empty'''
    p[0] = len(quad_gen.Quads)

def p_GotoFFor(p):
    '''GotoFFor : empty'''
    condition = get_operand_name(p[-1])  
    gotof_index = quad_gen.generate_gotof_quad(condition)
    p[0] = gotof_index

       
def p_empty(p):
    'empty :'
    p[0] = None
    
def p_error(p):
    if p:
        print(f"Error sintactico en '{p.value}', liea {p.lineno}, token de tipe: {p.type}")
        error_msg = f"Error sintactico '{p.value}' en la linea {p.lineno}"
    else:
        print("Error sintactico en EOF")
        error_msg = "Error sintactico en EOF"
    raise SyntaxError(error_msg)
        
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
        raise SyntaxError("error_msg: token invalido {token}")
        
def set_expr_type(expr_node, expr_type):
    if isinstance(expr_node, tuple):
        for i in range(len(expr_node)):
            if expr_node[i] == 'type':
                return expr_node[:i] + ('type', expr_type) + expr_node[i+2:]
        expr_node = expr_node + ('type', expr_type)
    return expr_node
    
def get_expr_type(expr_node):
    if isinstance(expr_node, tuple):
        if expr_node[0] == 'temp_result':
            for i in range(len(expr_node) - 1):
                if expr_node[i] == 'type' and i + 1 < len(expr_node):
                    return expr_node[i + 1]
        
        for i in range(len(expr_node) - 1):
            if expr_node[i] == 'type' and i + 1 < len(expr_node):
                return expr_node[i + 1]
        if expr_node[0] == 'id':
            return semantic.check_variable(expr_node[1])
        elif expr_node[0] == 'constant':
            if len(expr_node) > 2:
                return expr_node[2]
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
                    return Type.ERROR
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
            return Type.ERROR
    return Type.ERROR
    
parser = yacc.yacc(debug=False)

def parse_program(code):
    global semantic
    semantic = SemanticAnalyzer()
    global quad_gen
    quad_gen = QuadrupleGenerator(semantic)
    result = parser.parse(code)
    return result, semantic.error_list

def execute_program(code):
    from virtual_machine import VirtualMachine
    result, errors = parse_program(code)
    
    if errors:
        print("ERRORES SEMÁNTICOS:")
        for error in errors:
            print(f"  {error}")
        return None
    execution_data = quad_gen.get_execution_data()
    vm = VirtualMachine(
        execution_data['quadruples'],
        execution_data['constants_table'],
        execution_data['function_directory']
    )
    vm.execute()
    vm.print_memory_state()
    vm.print_program_outputs()
    
    return vm
    
if __name__ == "__main__":
    test_code = """
program operaciones_basicas;
var
    a, b, c, resultado, resultado2 : int;
    resultado3 : float;

main {
    a = 5;
    b = 3;
    c = 2;
    
    resultado = a + b * c;
    print("Resultado 1: ", resultado);
    
    resultado2 = (a + b) * c;
    print("Resultado 2: ", resultado2);
    
    resultado3 = a - b / c;
    print("Resultado 3: ", resultado3);
    
    resultado = a + b + c;
    print("Resultado 4: ", resultado);
    
    resultado2 = a + b * c * 2;
    print("Resultado 5: ", resultado2);
    
    resultado3 = a + b + c * 2;
    print("Resultado 6: ", resultado3);
    
    resultado3 = a  - b * c *2 + 1 ;
    print("Resultado 7: ", resultado3);
}
end
"""
    execute_program(test_code)
