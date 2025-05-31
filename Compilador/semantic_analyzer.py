from semantic_cube import Type,Operation,get_result_type
from MemoryManager import MemoryManager
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
        self.function_directory = {}
        self.global_vars = {}
        self.current_scope = "global"
        self.temp_vars = []
        self.current_type = None
        self.error_list = []
        self.program_name = None
        self.allow_function_redefinition = False
        self.scope_stack = ["global"]
        self.memory_manager = MemoryManager() 
        
    def add_error(self,message):
        self.error_list.append(f"Error semántico: {message}")
        print(f"ERROR SEMÁNTICO: {message}")
        return False
    
    def program_start(self,program_id):
        self.program_name=program_id
        self.current_scope="global"
        self.scope_stack=["global"]
        print(f"Programa {program_id} iniciado, ámbito reiniciado a global")
        return True
    
    def declare_main(self):
        if "main" in self.function_directory:
            return self.add_error("Función 'main' ya declarada")
        main_function=Function("main",Type.VOID)
        self.function_directory["main"]=main_function
        self.push_scope("main")
        print("Función main declarada, ámbito cambiado a main")
        if not "main" in self.function_directory:
            return self.add_error("Función 'main' no fue declarada previamente")
        return True
    
    def end_main(self):
        if "main" not in self.function_directory:
            return self.add_error("No se puede terminar la función main que no ha sido declarada")
        if self.current_scope == "main":
            self.pop_scope()
            print("Cuerpo de función main terminado, regresado al ámbito global")
        return True
    
    def program_end(self):
        if "main" not in self.function_directory:return self.add_error("El programa debe tener una función 'main'")
        print(f"Programa {self.program_name} completado")
        return True
    
    def start_var_declaration(self):
        self.temp_vars=[]
        print(f"Iniciando declaración de variables en ámbito '{self.current_scope}'")
        return True
    
    def add_id_to_temp_list(self,var_id):
        print(f"Agregando ID '{var_id}' a lista temporal en ámbito: {self.current_scope}")
        if var_id in self.temp_vars:return self.add_error(f"Variable '{var_id}' declarada múltiples veces en la misma declaración")
        if self.current_scope!="global":
            if var_id in self.function_directory[self.current_scope].local_vars:
                return self.add_error(f"Variable '{var_id}' ya declarada en ámbito '{self.current_scope}'")
        else:
            if var_id in self.global_vars:return self.add_error(f"Variable '{var_id}' ya declarada en ámbito global")
        self.temp_vars.append(var_id)
        print(f"'{var_id}' agregado a lista temporal de variables en ámbito: {self.current_scope}")
        return True
    
    def set_current_type(self, var_type):
        if var_type == "int":
            self.current_type = Type.INT
        elif var_type == "float":
            self.current_type = Type.FLOAT
        else:
            return self.add_error(f"Tipo no soportado: {var_type}. Solo 'int' y 'float' están permitidos para declaraciones de variables.")
        print(f"Tipo actual establecido a {self.current_type}")
        return True
    
    def start_scope(self,scope_name):
        self.push_scope(scope_name)
        if scope_name in self.function_directory:self.function_directory[scope_name].processing_locals=True
        print(f"Ámbito iniciado: {scope_name}")
        return True
    
    def end_scope(self):
        if self.current_scope!="global" and self.current_scope in self.function_directory:
            self.function_directory[self.current_scope].processing_locals=False
        old_scope=self.current_scope
        self.pop_scope()
        print(f"Ámbito terminado: {old_scope}, regresado a: {self.current_scope}")
        return True
    
    def add_vars_to_table(self):
        if not self.temp_vars:
            return True
        print(f"Agregando variables a tabla en ámbito: {self.current_scope}")
        for var_id in self.temp_vars:
            if self.current_scope == "global":
                if var_id in self.global_vars:
                    return self.add_error(f"Variable '{var_id}' ya declarada en ámbito global")
                new_var = Variable(var_id, self.current_type, "global")
                new_var.address = self.memory_manager.get_address(self.current_type, "global")
                self.global_vars[var_id] = new_var
                print(f"Variable global '{var_id}' agregada de tipo {self.current_type} en dirección {new_var.address}")
            else:
                if self.current_scope not in self.function_directory:
                    return self.add_error(f"Error interno: Función '{self.current_scope}' no encontrada en directorio")
                if var_id in self.function_directory[self.current_scope].local_vars:
                    return self.add_error(f"Variable '{var_id}' ya declarada en ámbito '{self.current_scope}'")
                new_var = Variable(var_id, self.current_type, self.current_scope)
                new_var.address = self.memory_manager.get_address(self.current_type, self.current_scope)
                self.function_directory[self.current_scope].local_vars[var_id] = new_var
                self.function_directory[self.current_scope].variables.append(new_var)
                self.function_directory[self.current_scope].var_count += 1
                print(f"Variable local '{var_id}' agregada de tipo {self.current_type} en dirección {new_var.address} a función '{self.current_scope}'")
        self.temp_vars = []
        return True
    
    def declare_function(self, func_id, return_type=Type.VOID):
        if func_id in self.function_directory and not self.allow_function_redefinition:
            return self.add_error(f"Función '{func_id}' ya declarada")
        
        new_function = Function(func_id, return_type)  # Pasar el return_type
        self.function_directory[func_id] = new_function
        self.push_scope(func_id)
        print(f"Función '{func_id}' declarada con tipo de retorno {return_type}, ámbito cambiado a: {self.current_scope}")
        return True
    
    def add_parameter(self, param_id, param_type):
        if self.current_scope == "global":
            return self.add_error("No se pueden declarar parámetros en ámbito global")
        if param_type == "int":
            type_enum = Type.INT
        elif param_type == "float":
            type_enum = Type.FLOAT
        else:
            print(f"Error: Tipo de parámetro inválido '{param_type}' en función '{self.current_scope}'")
            type_enum = Type.ERROR
            self.add_error(f"Tipo de parámetro no soportado: '{param_type}' en función '{self.current_scope}'. Solo 'int' y 'float' están permitidos.")
        if param_id in self.function_directory[self.current_scope].local_vars:
            return self.add_error(f"Parámetro '{param_id}' ya declarado en función '{self.current_scope}'")
        param_var = Variable(param_id, type_enum, self.current_scope)
        param_var.address = self.memory_manager.get_address(type_enum, self.current_scope)
        self.function_directory[self.current_scope].add_parameter(param_var)
        print(f"Parámetro '{param_id}' agregado de tipo {type_enum} en dirección {param_var.address} a función '{self.current_scope}'")
        return True

    def end_function_declaration(self):
        if self.current_scope=="global":return self.add_error("No está dentro de una declaración de función")
        func_name=self.current_scope
        self.pop_scope()
        print(f"Declaración de función '{func_name}' terminada, regresado al ámbito: {self.current_scope}")
        return True
    
    def check_variable(self,var_id):
        if self.current_scope!="global" and var_id in self.function_directory[self.current_scope].local_vars:
            return self.function_directory[self.current_scope].local_vars[var_id].type
        if var_id in self.global_vars:
            return self.global_vars[var_id].type
        self.add_error(f"Variable '{var_id}' no declarada")
        return Type.ERROR
    
    def check_function(self,func_id):
        if func_id in self.function_directory:return self.function_directory[func_id]
        self.add_error(f"Función '{func_id}' no declarada")
        return None
    
    def check_assignment_compatibility(self,var_id,expr_type):
        var_type=self.check_variable(var_id)
        if var_type==Type.ERROR:return False
        result_type=get_result_type(var_type,expr_type,Operation.ASSIGN)
        if result_type==Type.ERROR:
            return self.add_error(f"Tipos incompatibles en asignación a '{var_id}': No se puede asignar {expr_type} a {var_type}")
        return True
    
    def check_expression_compatibility(self,left_type,right_type,operation):
        result_type=get_result_type(left_type,right_type,operation)
        if result_type==Type.ERROR:
            self.add_error(f"Tipos incompatibles en operación {operation}: {left_type} y {right_type}")
        return result_type
    
    def check_condition(self,expr_type):
        if expr_type!=Type.BOOL:
            return self.add_error(f"Expresión de condición debe ser booleana, obtuvo {expr_type}")
        return True
    
    def print_function_directory(self):
        print("\n===== DIRECTORIO DE FUNCIONES =====")
        for func_name,func in self.function_directory.items():
            print(f"{func}")
            print("  Parámetros:")
            for param in func.parameters:print(f"    {param}")
            print("  Variables Locales:")
            for var in func.variables:print(f"    {var}")
        print("\n===== VARIABLES GLOBALES =====")
        for var_name,var in self.global_vars.items():print(f"  {var}")
        if self.error_list:
            print("\n===== ERRORES SEMÁNTICOS =====")
            for error in self.error_list:
                print(f"  {error}")
            
    def push_scope(self,new_scope):
        self.scope_stack.append(new_scope)
        self.current_scope=new_scope
        print(f"Ámbito agregado: {new_scope}, pila de ámbitos actual: {self.scope_stack}")
        return True
    
    def pop_scope(self):
        if len(self.scope_stack)>1:
            old_scope=self.scope_stack.pop()
            self.current_scope=self.scope_stack[-1]
            print(f"Ámbito removido: {old_scope}, ámbito actual es ahora: {self.current_scope}")
            return True
        else:
            self.add_error("No se puede remover el ámbito global")
            return False
        
    def get_function_start_address(self, func_name):
        if func_name in self.function_directory:
            return self.function_directory[func_name].start_address
        return None