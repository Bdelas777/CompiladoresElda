import ply.yacc as yacc
from lex import tokens
from semantic_cube import Type,Operation,get_result_type
from semantic_analyzer import SemanticAnalyzer
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger=logging.getLogger('BabyDuck')
semantic=SemanticAnalyzer()

def p_programa(p):
    '''programa : TOKEN_PROGRAM TOKEN_ID TOKEN_SEMICOLON dec_var dec_funcs TOKEN_MAIN body TOKEN_END'''
    semantic.program_start(p[2])
    semantic.declare_main()
    p[0]=('programa',p[2],p[4],p[5],p[7])
    semantic.end_main()
    semantic.program_end()
    
def p_dec_var(p):
    '''dec_var : vars
    | empty'''
    p[0]=p[1]
def p_dec_funcs(p):
    '''dec_funcs : funcs dec_funcs
    | empty'''
    if p[1]==None:p[0]=[]
    else:
        if isinstance(p[2],list):p[0]=[p[1]]+p[2]
        else:p[0]=[p[1]]
        
def p_vars(p):
    '''vars : TOKEN_VAR variable rep_var'''
    semantic.start_var_declaration()
    if p[3]==None:
        p[0]=('vars',[p[2]])
    else:
        p[0]=('vars',[p[2]]+p[3])
        
def p_rep_var(p):
    '''rep_var  : variable rep_var
    |  empty'''
    if p[1]==None:
        p[0]=None
    else:
        if p[2]==None:p[0]=[p[1]]
        else:p[0]=[p[1]]+p[2]
        
def p_variable(p):
    '''variable : TOKEN_ID mas_ids TOKEN_COLON type TOKEN_SEMICOLON'''
    semantic.add_id_to_temp_list(p[1])
    ids=[p[1]]+(p[2] if p[2] else[])
    for id in ids[1:]:
        semantic.add_id_to_temp_list(id)
    semantic.set_current_type(p[4])
    semantic.add_vars_to_table()
    p[0]=('variable',ids,p[4])
def p_mas_ids(p):
    '''mas_ids : TOKEN_COMMA TOKEN_ID mas_ids
    |  empty'''
    if p[1]==None:p[0]=[]
    else:
        if p[3]==None:
            p[0]=[p[2]]
        else:
            p[0]=[p[2]]+p[3]
            
def p_type(p):
    '''type : TOKEN_INT
    | TOKEN_FLOAT'''
    p[0]=p[1]
def p_body(p):
    '''body : TOKEN_LBRACE dec_statements TOKEN_RBRACE'''
    p[0]=('body',p[2] if p[2] else[])
def p_dec_statements(p):
    '''dec_statements : statement dec_statements
    | empty'''
    if p[1]==None:p[0]=[]
    else:
        if isinstance(p[2],list):p[0]=[p[1]]+p[2]
        else:p[0]=[p[1]]
def p_statement(p):
    '''statement : assign
        | condition
        | cycle
        | f_call
        | print'''
    p[0]=p[1]
def p_print(p):
    '''print : TOKEN_PRINT TOKEN_LPAREN expresiones TOKEN_RPAREN TOKEN_SEMICOLON'''
    p[0]=('print',p[3])
def p_expresiones(p):
    '''expresiones : TOKEN_CTE_STRING comas
    | expresion comas'''
    if isinstance(p[1],str):
        p[0]=[('string',p[1])]+(p[2] if p[2] else[])
    else:
        p[0]=[p[1]]+(p[2] if p[2] else[])
        
def p_comas(p):
    '''comas : TOKEN_COMMA expresion comas
    | TOKEN_COMMA TOKEN_CTE_STRING comas
    | empty'''
    if p[1]==None:
        p[0]=[]
    elif p[2]=='TOKEN_CTE_STRING' or isinstance(p[2],str):
        value=p[2] if isinstance(p[2],str) else 'unknown'
        p[0]=[('string',value)]+(p[3] if p[3] else[])
    else:
        p[0]=[p[2]]+(p[3] if p[3] else[])
        
def p_cycle(p):
    '''cycle : TOKEN_WHILE TOKEN_LPAREN expresion TOKEN_RPAREN TOKEN_DO body TOKEN_SEMICOLON'''
    expr_type=get_expr_type(p[3])
    semantic.check_condition(expr_type)
    p[0]=('while',p[3],p[6])
    
def p_condition(p):
    '''condition : TOKEN_IF TOKEN_LPAREN expresion TOKEN_RPAREN body else TOKEN_SEMICOLON'''
    expr_type=get_expr_type(p[3])
    semantic.check_condition(expr_type)
    p[0]=('if',p[3],p[5],p[6])
def p_else(p):
    '''else : TOKEN_ELSE body
    | empty'''
    if p[1]==None:
        p[0]=None
    else:
        p[0]=p[2]
def p_cte(p):
    '''cte : TOKEN_CTE_INT
    | TOKEN_CTE_FLOAT'''
    p[0]=('constant',p[1])
    
def p_expresion(p):
    '''expresion : exp comparar'''
    if p[2]==None:
        p[0]=p[1]
    else:
        left_type=get_expr_type(p[1])
        right_type=get_expr_type(p[2][1])
        op=token_to_operation(p[2][0])
        result_type=semantic.check_expression_compatibility(left_type,right_type,op)
        p[0]=('comparison',p[1],p[2][0],p[2][1])
        p[0]=set_expr_type(p[0],result_type)
        
def p_comparar(p):
    '''comparar  : signo exp
    | empty'''
    if p[1]==None:
        p[0]=None
    else:
        p[0]=(p[1],p[2])
        
def p_signo(p):
    '''signo : TOKEN_GT
    | TOKEN_LT
    | TOKEN_NE'''
    p[0]=p[1]
def p_exp(p):
    '''exp  : termino suma_resta'''
    if p[2]==None:
        p[0]=p[1]
    else:
        left_type=get_expr_type(p[1])
        right_type=get_expr_type(p[2][1])
        op=token_to_operation(p[2][0])
        result_type=semantic.check_expression_compatibility(left_type,right_type,op)
        p[0]=('operation',p[1],p[2][0],p[2][1])
        p[0]=set_expr_type(p[0],result_type)
        
def p_suma_resta(p):
    '''suma_resta : TOKEN_PLUS termino suma_resta
    | TOKEN_MINUS termino suma_resta
    | empty'''
    if p[1]==None:
        p[0]=None
    else:
        if p[3]==None:p[0]=(p[1],p[2])
        else:
            p[0]=(p[1],('operation',p[2],p[3][0],p[3][1]) if isinstance(p[3],tuple) and len(p[3])>1 else p[2])
def p_termino(p):
    '''termino : factor multi_div'''
    if p[2]==None:
        p[0]=p[1]
    else:
        left_type=get_expr_type(p[1])
        right_type=get_expr_type(p[2][1])
        op=token_to_operation(p[2][0])
        result_type=semantic.check_expression_compatibility(left_type,right_type,op)
        p[0]=('operation',p[1],p[2][0],p[2][1])
        p[0]=set_expr_type(p[0],result_type)
        
def p_multi_div(p):
    '''multi_div  : operacion_mul_div factor multi_div  
    | empty'''
    if p[1]==None:
        p[0]=None
    else:
        if p[3]==None:
            p[0]=(p[1],p[2])
        else:
            p[0]=(p[1],('operation',p[2],p[3][0],p[3][1]) if isinstance(p[3],tuple) and len(p[3])>1 else p[2])
            
def p_operacion_mul_div(p):
    '''operacion_mul_div : TOKEN_DIV
    | TOKEN_MULT'''
    p[0]=p[1]
def p_factor(p):
    '''factor : definicion
    | operaciones'''
    p[0]=p[1]
def p_definicion(p):
    '''definicion : TOKEN_LPAREN expresion TOKEN_RPAREN'''
    p[0]=p[2]
def p_operaciones(p):
    '''operaciones : opciones_mas_menos id_cte'''
    if p[1]==None:
        p[0]=p[2]
    else:
        expr_type=get_expr_type(p[2])
        if expr_type not in[Type.INT,Type.FLOAT]:semantic.add_error(f"Unary operation not supported for type {expr_type}")
        p[0]=('unary',p[1],p[2])
        p[0]=set_expr_type(p[0],expr_type)
def p_opciones_mas_menos(p):
    '''opciones_mas_menos : TOKEN_PLUS
    | TOKEN_MINUS
    | empty'''
    p[0]=p[1]
def p_id_cte(p):
    '''id_cte : TOKEN_ID
    | cte'''
    if isinstance(p[1],tuple):
        p[0]=p[1]
    else:
        if p[1] and p.slice[1].type=='TOKEN_ID':
            var_type=semantic.check_variable(p[1])
            p[0]=('id',p[1])
            p[0]=set_expr_type(p[0],var_type)
        else:
            if p.slice[1].type=='cte':p[0]=p[1]
            else:p[0]=('id',p[1])
def p_funcs(p):
    '''funcs :  TOKEN_VOID TOKEN_ID scopefun TOKEN_LPAREN tipo TOKEN_RPAREN TOKEN_LCOL var body TOKEN_RCOL TOKEN_SEMICOLON'''
    # Get the function object that was established in scopefun
    func = semantic.check_function(p[2])
    
    # Process parameters from tipo
    params = p[5] if p[5] else []
    if isinstance(params, list):
        for param in params:
            if isinstance(param, tuple) and param[0] == 'param':
                semantic.add_parameter(param[1], param[2])
    
    # Store the function with its body and variables
    p[0] = ('function', p[2], p[5] if p[5] else [], p[7], p[8])
    
    # End function declaration and return to global scope
    semantic.end_function_declaration()

def p_scopefun(p):
    '''scopefun : empty'''
    # Get the function name from the previous token
    function_name = p[-1]
    
    # Declare the function and set current scope to this function
    semantic.declare_function(function_name)
    
    print(f"Function scope established: {function_name}")
    return True
    
def p_tipo(p):
    '''tipo : def_tipo
    | empty'''
    p[0]=p[1]
def p_def_tipo(p):
    '''def_tipo : TOKEN_ID TOKEN_COLON type coma'''
    if p[4]==None:
        p[0]=[('param',p[1],p[3])]
    else:
        p[0]=[('param',p[1],p[3])]+p[4]
def p_coma(p):
    '''coma : TOKEN_COMMA TOKEN_ID TOKEN_COLON type coma
    | empty'''
    if p[1]==None:
        p[0]=None
    else:
        new_param=('param',p[2],p[4])
        if p[5]==None:
            p[0]=[new_param]
        else:
            p[0]=[new_param]+p[5]
            
def p_var(p):
    '''var : vars 
    | empty'''
    p[0]=p[1]
    
def p_f_call(p):
    '''f_call : TOKEN_ID TOKEN_LPAREN def_exp TOKEN_RPAREN TOKEN_SEMICOLON'''
    func=semantic.check_function(p[1])
    if func:
        args=p[3] if p[3] else[]
        if len(args)!=len(func.parameters):
            semantic.add_error(f"Function '{p[1]}' expects {len(func.parameters)} arguments, got {len(args)}")
        else:
            for i,(arg,param) in enumerate(zip(args,func.parameters)):
                arg_type=get_expr_type(arg)
                param_type=param.type
                result_type=get_result_type(param_type,arg_type,Operation.ASSIGN)
                if result_type==Type.ERROR:
                    semantic.add_error(f"Parameter type mismatch in call to '{p[1]}': Parameter {i+1} expects {param_type}, got {arg_type}")
    p[0]=('function_call',p[1],p[3] if p[3] else[])
def p_def_exp(p):
    '''def_exp : expresion coma2
    | empty'''
    if p[1]==None:p[0]=[]
    else:p[0]=[p[1]]+(p[2] if p[2] else[])
def p_coma2(p):
    '''coma2 : TOKEN_COMMA expresion coma2
    | empty'''
    if p[1]==None:
        p[0]=[]
    else:
        p[0]=[p[2]]+(p[3] if p[3] else[])
def p_assign(p):
    '''assign : TOKEN_ID TOKEN_ASSIGN expresion TOKEN_SEMICOLON'''
    var_type=semantic.check_variable(p[1])
    expr_type=get_expr_type(p[3])
    semantic.check_assignment_compatibility(p[1],expr_type)
    p[0]=('assign',p[1],p[3])
def p_empty(p):
    'empty :'
    p[0]=None
def p_error(p):
    if p:
        logger.error(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        logger.error("Syntax error at EOF")
def token_to_operation(token):
    if token=='+' or token=='TOKEN_PLUS':return Operation.PLUS
    elif token=='-' or token=='TOKEN_MINUS':return Operation.MINUS
    elif token=='*' or token=='TOKEN_MULT':return Operation.MULTIPLY
    elif token=='/' or token=='TOKEN_DIV':return Operation.DIVIDE
    elif token=='>' or token=='TOKEN_GT':return Operation.GREATER
    elif token=='<' or token=='TOKEN_LT':return Operation.LESS
    elif token=='!=' or token=='TOKEN_NE':return Operation.NOT_EQUAL
    elif token=='=' or token=='TOKEN_ASSIGN':return Operation.ASSIGN
    else:return None
def set_expr_type(expr_node,expr_type):
    if isinstance(expr_node,tuple):expr_node=expr_node+('type',expr_type)
    return expr_node
def get_expr_type(expr_node):
    if isinstance(expr_node,tuple):
        for i in range(len(expr_node)-1):
            if expr_node[i]=='type' and i+1<len(expr_node):
                return expr_node[i+1]
        if expr_node[0]=='id':
            return semantic.check_variable(expr_node[1])
        elif expr_node[0]=='constant':
            if isinstance(expr_node[1],int):return Type.INT
            elif isinstance(expr_node[1],float):return Type.FLOAT
            elif isinstance(expr_node[1],str):
                try:
                    float(expr_node[1])
                    if '.' in expr_node[1]:return Type.FLOAT
                    else:return Type.INT
                except:return Type.STRING
        elif expr_node[0]=='operation':
            left_type=get_expr_type(expr_node[1])
            right_type=get_expr_type(expr_node[3])
            op=token_to_operation(expr_node[2])
            return get_result_type(left_type,right_type,op)
        elif expr_node[0]=='comparison':
            return Type.BOOL
        elif expr_node[0]=='function_call_expr':
            func=semantic.check_function(expr_node[1])
            if func:
                return func.return_type
    return Type.ERROR
parser=yacc.yacc(debug=False)
def parse_program(code):
    global semantic
    semantic=SemanticAnalyzer()
    result=parser.parse(code)
    return result,semantic.error_list
if __name__=="__main__":
    data='''
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
    result=parser.parse(data)