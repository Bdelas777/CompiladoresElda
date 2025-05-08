from semantic_cube import Type,Operation,get_result_type

class Variable:
    def __init__(self,name,var_type,scope="global"):
        self.name=name
        self.type=var_type
        self.scope=scope
        self.address=None
    def __str__(self):
        return f"Variable(name={self.name}, type={self.type}, scope={self.scope})"
    
class Function:
    
    def __init__(self,name,return_type=Type.VOID):
        self.name=name
        self.return_type=return_type
        self.parameters=[]
        self.local_vars={}
        self.variables=[]
        self.param_count=0
        self.var_count=0
        self.temp_count=0
        self.start_address=None
        self.processing_locals=False
        
    def add_parameter(self,param_var):
        self.parameters.append(param_var)
        self.local_vars[param_var.name]=param_var
        self.param_count+=1
        
    def add_local_var(self,var_name,var_type):
        if var_name in self.local_vars:return False
        new_var=Variable(var_name,var_type,self.name)
        self.local_vars[var_name]=new_var
        self.variables.append(new_var)
        self.var_count+=1
        return True
    
    def __str__(self):
        return f"Function(name={self.name}, return_type={self.return_type}, params={len(self.parameters)}, vars={len(self.local_vars)})"

class SemanticAnalyzer:
    def __init__(self):
        self.function_directory={}
        self.global_vars={}
        self.current_scope="global"
        self.temp_vars=[]
        self.current_type=None
        self.error_list=[]
        self.program_name=None
        self.allow_function_redefinition=False
        self.scope_stack=["global"]
        
    def add_error(self,message):
        self.error_list.append(f"Semantic error: {message}")
        print(f"SEMANTIC ERROR: {message}")
        return False
    
    def program_start(self,program_id):
        self.program_name=program_id
        self.current_scope="global"
        self.scope_stack=["global"]
        print(f"Program {program_id} started, scope reset to global")
        return True
    
    def declare_main(self):
        if "main" in self.function_directory:return self.add_error("Function 'main' already declared")
        main_function=Function("main",Type.VOID)
        self.function_directory["main"]=main_function
        self.push_scope("main")
        print("Main function declared, scope changed to main")
        return True
    
    def end_main(self):
        if "main" not in self.function_directory:return self.add_error("Cannot end main function that hasn't been declared")
        self.pop_scope()
        print("Main function body ended, returned to global scope")
        return True
    
    def program_end(self):
        if "main" not in self.function_directory:return self.add_error("Program must have a 'main' function")
        print(f"Program {self.program_name} completed")
        return True
    
    def start_var_declaration(self):
        self.temp_vars=[]
        print(f"Starting variable declaration in scope '{self.current_scope}'")
        return True
    
    def add_id_to_temp_list(self,var_id):
        print(f"Adding ID '{var_id}' to temp list in scope: {self.current_scope}")
        if var_id in self.temp_vars:return self.add_error(f"Variable '{var_id}' declared multiple times in the same declaration")
        if self.current_scope!="global":
            if var_id in self.function_directory[self.current_scope].local_vars:
                return self.add_error(f"Variable '{var_id}' already declared in scope '{self.current_scope}'")
        else:
            if var_id in self.global_vars:return self.add_error(f"Variable '{var_id}' already declared in global scope")
        self.temp_vars.append(var_id)
        print(f"Added '{var_id}' to temporary variable list in scope: {self.current_scope}")
        return True
    
    def set_current_type(self,var_type):
        if var_type=="int":self.current_type=Type.INT
        elif var_type=="float":self.current_type=Type.FLOAT
        elif var_type=="bool":self.current_type=Type.BOOL
        elif var_type=="string":self.current_type=Type.STRING
        else:return self.add_error(f"Unsupported type: {var_type}")
        print(f"Set current type to {self.current_type}")
        return True
    
    def start_scope(self,scope_name):
        self.push_scope(scope_name)
        if scope_name in self.function_directory:self.function_directory[scope_name].processing_locals=True
        print(f"Started scope: {scope_name}")
        return True
    
    def end_scope(self):
        if self.current_scope!="global" and self.current_scope in self.function_directory:
            self.function_directory[self.current_scope].processing_locals=False
        old_scope=self.current_scope
        self.pop_scope()
        print(f"Ended scope: {old_scope}, returned to: {self.current_scope}")
        return True
    
    def add_vars_to_table(self):
        if not self.temp_vars:return True
        print(f"Adding variables to table in scope: {self.current_scope}")
        for var_id in self.temp_vars:
            if self.current_scope=="global":
                if var_id in self.global_vars:return self.add_error(f"Variable '{var_id}' already declared in global scope")
                self.global_vars[var_id]=Variable(var_id,self.current_type,"global")
                print(f"Added global variable '{var_id}' of type {self.current_type}")
            else:
                if self.current_scope not in self.function_directory:
                    return self.add_error(f"Internal error: Function '{self.current_scope}' not found in directory")
                if var_id in self.function_directory[self.current_scope].local_vars:
                    return self.add_error(f"Variable '{var_id}' already declared in scope '{self.current_scope}'")
                success=self.function_directory[self.current_scope].add_local_var(var_id,self.current_type)
                if not success:
                    return self.add_error(f"Variable '{var_id}' already declared in scope '{self.current_scope}'")
                print(f"Added local variable '{var_id}' of type {self.current_type} to function '{self.current_scope}'")
        self.temp_vars=[]
        return True
    
    def declare_function(self,func_id,return_type=Type.VOID):
        if func_id in self.function_directory and not self.allow_function_redefinition:
            return self.add_error(f"Function '{func_id}' already declared")
        new_function=Function(func_id,return_type)
        self.function_directory[func_id]=new_function
        self.push_scope(func_id)
        print(f"Declared function '{func_id}' with return type {return_type}, scope changed to: {self.current_scope}")
        return True
    
    def add_parameter(self, param_id, param_type):
        if self.current_scope == "global":
            return self.add_error("Cannot declare parameters in global scope")
        
        # Validar el tipo de parámetro de manera más robusta
        if param_type == "int":
            type_enum = Type.INT
        elif param_type == "float":
            type_enum = Type.FLOAT
        elif param_type == "bool":
            type_enum = Type.BOOL
        elif param_type == "string":
            type_enum = Type.STRING
        else:
            print(f"Error: Tipo de parámetro inválido '{param_type}' en función '{self.current_scope}'")
            # Asignar un tipo por defecto para evitar que se cicle
            type_enum = Type.ERROR
            # Seguir procesando pero marcar el error
            self.add_error(f"Unsupported parameter type: '{param_type}' in function '{self.current_scope}'")
        
        if param_id in self.function_directory[self.current_scope].local_vars:
            return self.add_error(f"Parameter '{param_id}' already declared in function '{self.current_scope}'")
        
        param_var = Variable(param_id, type_enum, self.current_scope)
        self.function_directory[self.current_scope].add_parameter(param_var)
        print(f"Added parameter '{param_id}' of type {type_enum} to function '{self.current_scope}'")
        return True

    
    def end_function_declaration(self):
        if self.current_scope=="global":return self.add_error("Not inside a function declaration")
        func_name=self.current_scope
        self.pop_scope()
        print(f"Ended function '{func_name}' declaration, returned to scope: {self.current_scope}")
        return True
    
    def check_variable(self,var_id):
        if self.current_scope!="global" and var_id in self.function_directory[self.current_scope].local_vars:
            return self.function_directory[self.current_scope].local_vars[var_id].type
        if var_id in self.global_vars:
            return self.global_vars[var_id].type
        self.add_error(f"Variable '{var_id}' not declared")
        return Type.ERROR
    
    def check_function(self,func_id):
        if func_id in self.function_directory:return self.function_directory[func_id]
        self.add_error(f"Function '{func_id}' not declared")
        return None
    
    def check_assignment_compatibility(self,var_id,expr_type):
        var_type=self.check_variable(var_id)
        if var_type==Type.ERROR:return False
        result_type=get_result_type(var_type,expr_type,Operation.ASSIGN)
        if result_type==Type.ERROR:
            return self.add_error(f"Incompatible types in assignment to '{var_id}': Cannot assign {expr_type} to {var_type}")
        return True
    
    def check_expression_compatibility(self,left_type,right_type,operation):
        result_type=get_result_type(left_type,right_type,operation)
        if result_type==Type.ERROR:
            self.add_error(f"Incompatible types in operation {operation}: {left_type} and {right_type}")
        return result_type
    
    def check_condition(self,expr_type):
        if expr_type!=Type.BOOL:
            return self.add_error(f"Condition expression must be boolean, got {expr_type}")
        return True
    
    def print_function_directory(self):
        print("\n===== FUNCTION DIRECTORY =====")
        for func_name,func in self.function_directory.items():
            print(f"{func}")
            print("  Parameters:")
            for param in func.parameters:print(f"    {param}")
            print("  Local Variables:")
            for var in func.variables:print(f"    {var}")
        print("\n===== GLOBAL VARIABLES =====")
        for var_name,var in self.global_vars.items():print(f"  {var}")
        if self.error_list:
            print("\n===== SEMANTIC ERRORS =====")
            for error in self.error_list:
                print(f"  {error}")
            
    def push_scope(self,new_scope):
        self.scope_stack.append(new_scope)
        self.current_scope=new_scope
        print(f"Pushed scope: {new_scope}, current scope stack: {self.scope_stack}")
        return True
    
    def pop_scope(self):
        if len(self.scope_stack)>1:
            old_scope=self.scope_stack.pop()
            self.current_scope=self.scope_stack[-1]
            print(f"Popped scope: {old_scope}, current scope is now: {self.current_scope}")
            return True
        else:
            self.add_error("Cannot pop global scope")
            return False