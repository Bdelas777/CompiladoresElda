from semantic_cube import Type, Operation, get_result_type

class Variable:
    def __init__(self, name, var_type, scope="global"):
        self.name = name
        self.type = var_type
        self.scope = scope
        self.address = None  # Para asignar dirección de memoria

    def __str__(self):
        return f"Variable(name={self.name}, type={self.type}, scope={self.scope})"

class Function:
    def __init__(self, name, return_type=Type.VOID):
        self.name = name
        self.return_type = return_type
        self.parameters = []  # Lista de Variables que son parámetros
        self.local_vars = {}  # Diccionario de variables locales
        self.param_count = 0
        self.var_count = 0
        self.temp_count = 0
        self.start_address = None  # Dirección de inicio en cuádruplos
        self.processing_locals = False  # Flag para saber si estamos procesando variables locales

    def add_parameter(self, param_var):
        self.parameters.append(param_var)
        self.local_vars[param_var.name] = param_var
        self.param_count += 1
        
    def add_local_var(self, var_name, var_type):
        if var_name in self.local_vars:
            return False  # Variable ya declarada
        
        new_var = Variable(var_name, var_type, self.name)
        self.local_vars[var_name] = new_var
        self.var_count += 1
        return True

    def __str__(self):
        return f"Function(name={self.name}, return_type={self.return_type}, params={len(self.parameters)}, vars={len(self.local_vars)})"

class SemanticAnalyzer:
    def __init__(self):
        self.function_directory = {}  # Directorio de funciones
        self.global_vars = {}  # Tabla de variables globales
        self.current_scope = "global"  # Ámbito actual
        self.temp_vars = []  # Lista temporal de identificadores para declaración
        self.current_type = None  # Tipo actual para declaración de variables
        self.error_list = []  # Lista de errores semánticos
        self.program_name = None  # Nombre del programa
        self.allow_function_redefinition = False  # Bandera para permitir redefiniciones
        self.scope_stack = ["global"]  # Pila para seguir los ámbitos anidados

    def add_error(self, message):
        """Añade un error a la lista de errores"""
        self.error_list.append(f"Semantic error: {message}")
        print(f"SEMANTIC ERROR: {message}")
        return False

    def program_start(self, program_id):
        """Punto P1 y P2: Inicialización del programa"""
        self.program_name = program_id
        self.current_scope = "global"
        self.scope_stack = ["global"]  # Reset scope stack
        print(f"Program {program_id} started, scope reset to global")
        return True

    def declare_main(self):
        """Punto P3: Declaración de la función main"""
        if "main" in self.function_directory:
            return self.add_error("Function 'main' already declared")
        
        main_function = Function("main", Type.VOID)
        self.function_directory["main"] = main_function
        self.push_scope("main")
        print("Main function declared, scope changed to main")
        return True

    def end_main(self):
        """Punto P4: Finalizar el cuerpo de main"""
        if "main" not in self.function_directory:
            return self.add_error("Cannot end main function that hasn't been declared")
            
        self.pop_scope()  # Return to global scope
        print("Main function body ended, returned to global scope")
        return True

    def program_end(self):
        """Punto P5: Finalización del programa"""
        if "main" not in self.function_directory:
            return self.add_error("Program must have a 'main' function")
        
        print(f"Program {self.program_name} completed")
        return True

    def start_var_declaration(self):
        """Punto V1: Inicio de declaración de variables"""
        self.temp_vars = []
        print(f"Starting variable declaration in scope '{self.current_scope}'")
        return True
    
    def prepare_for_parameters(self):
        """Punto F3: Preparar para recibir parámetros de la función"""
        # This is mostly a marker point as the actual parameter processing is done elsewhere
        print(f"Preparing to receive parameters for function '{self.current_scope}'")
        return True

    def finish_parameters(self):
        """Punto F4: Finalizar recepción de parámetros"""
        if self.current_scope == "global":
            return self.add_error("Cannot finish parameters in global scope")
        
        print(f"Finished receiving parameters for function '{self.current_scope}'")
        return True
    
    def finish_ids_collection(self):
        """Punto V3: Finalizar recopilación de identificadores para este tipo"""
        print(f"Finished collecting IDs in scope '{self.current_scope}', ready for type assignment")
        return True
    
    def add_id_to_temp_list(self, var_id):
        """Punto V2: Añadir identificador a lista temporal"""
        print(f"Adding ID '{var_id}' to temp list in scope: {self.current_scope}")
        
        # First check if this variable name is already in the temp list
        if var_id in self.temp_vars:
            return self.add_error(f"Variable '{var_id}' declared multiple times in the same declaration")
        # Si estamos procesando explícitamente variables locales de una función,
        # verificar duplicados solo en ese ámbito
        function_scope = None
        for func_name, func in self.function_directory.items():
            if hasattr(func, 'processing_locals') and func.processing_locals:
                function_scope = func_name
                break
        if function_scope:
            # Estamos procesando variables locales para una función específica
            if var_id in self.function_directory[function_scope].local_vars:
                return self.add_error(f"Variable '{var_id}' already declared in scope '{function_scope}'")
        else:
            # Para local scope, only check for duplicates within the same function
            if self.current_scope != "global":
                if var_id in self.function_directory[self.current_scope].local_vars:
                    return self.add_error(f"Variable '{var_id}' already declared in scope '{self.current_scope}'")
                # Variables in a function can have the same name as global variables - this is OK!
            else:
                # In global scope, check for duplicates in global vars
                if var_id in self.global_vars:
                    return self.add_error(f"Variable '{var_id}' already declared in global scope")
        # Add to the temporary list
        self.temp_vars.append(var_id)
        # Si estamos procesando variables locales de una función, actualizar el ámbito temporalmente
        if function_scope:
            print(f"Added '{var_id}' to temporary variable list in function scope: {function_scope}")
        else:
            print(f"Added '{var_id}' to temporary variable list in scope: {self.current_scope}")
        
        return True

    def enter_block(self, block_type="generic"):
        """Punto B1: Entering a block"""
        print(f"Entering {block_type} block in scope '{self.current_scope}'")
        return True

    def exit_block(self, block_type="generic"):
        """Punto B2: Exiting a block"""
        print(f"Exiting {block_type} block in scope '{self.current_scope}'")
        return True

    def set_current_type(self, var_type):
        """Punto V3 y V4: Establecer el tipo actual para las variables en la lista temporal"""
        if var_type == "int":
            self.current_type = Type.INT
        elif var_type == "float":
            self.current_type = Type.FLOAT
        elif var_type == "bool":
            self.current_type = Type.BOOL
        elif var_type == "string":
            self.current_type = Type.STRING
        else:
            return self.add_error(f"Unsupported type: {var_type}")
        print(f"Set current type to {self.current_type}")
        return True

    def start_scope(self, scope_name):
        """Iniciar un nuevo ámbito para declaración de variables"""
        self.push_scope(scope_name)
        # Marcar que estamos procesando variables locales en esta función
        if scope_name in self.function_directory:
            self.function_directory[scope_name].processing_locals = True
        print(f"Started scope: {scope_name}, processing locals: {self.function_directory.get(scope_name, None)}")
        return True

    def end_scope(self):
        """Finalizar el ámbito actual"""
        if self.current_scope != "global" and self.current_scope in self.function_directory:
            self.function_directory[self.current_scope].processing_locals = False
        old_scope = self.current_scope
        self.pop_scope()
        print(f"Ended scope: {old_scope}, returned to: {self.current_scope}")
        return True

    # Actualización del método add_vars_to_table para manejar mejor los scopes
    def add_vars_to_table(self):
        """Punto V5: Añadir variables en lista temporal a la tabla correspondiente"""
        if not self.temp_vars:
            return True  # No hay variables para añadir
        
        print(f"Adding variables to table in scope: {self.current_scope}")
        for var_id in self.temp_vars:
            if self.current_scope == "global":
                # Just double-check to prevent duplicates in global scope
                if var_id in self.global_vars:
                    return self.add_error(f"Variable '{var_id}' already declared in global scope")
                self.global_vars[var_id] = Variable(var_id, self.current_type, "global")
                print(f"Added global variable '{var_id}' of type {self.current_type}")
            else:
                # Verificar que la función actual existe en el directorio
                if self.current_scope not in self.function_directory:
                    return self.add_error(f"Internal error: Function '{self.current_scope}' not found in directory")
                    
                # Double-check to prevent duplicates in local scope
                if var_id in self.function_directory[self.current_scope].local_vars:
                    return self.add_error(f"Variable '{var_id}' already declared in scope '{self.current_scope}'")
                
                # Añadir la variable local a la función actual
                success = self.function_directory[self.current_scope].add_local_var(var_id, self.current_type)
                if not success:
                    return self.add_error(f"Variable '{var_id}' already declared in scope '{self.current_scope}'")
                print(f"Added local variable '{var_id}' of type {self.current_type} to function '{self.current_scope}'")
        
        # Limpiar la lista temporal
        self.temp_vars = []
        return True

    def declare_function(self, func_id, return_type=Type.VOID):
        """Punto F1 y F2: Declaración de función""" 
        self.push_scope(func_id)
        # Allow function overloading/redefinition based on requirements 
        if func_id in self.function_directory and not self.allow_function_redefinition:
            return self.add_error(f"Function '{func_id}' already declared")
        new_function = Function(func_id, return_type)
        self.function_directory[func_id] = new_function
        # Change scope to the newly declared function
       
        print(f"Declared function '{func_id}' with return type {return_type}, scope changed to: {self.current_scope}")
        return True

    def add_parameter(self, param_id, param_type):
        """Punto DT1 y DT2: Añadir parámetro a función actual"""
        if self.current_scope == "global":
            return self.add_error("Cannot declare parameters in global scope")
        # Convertir string de tipo a enum Type
        if param_type == "int":
            type_enum = Type.INT
        elif param_type == "float":
            type_enum = Type.FLOAT
        elif param_type == "bool":
            type_enum = Type.BOOL
        elif param_type == "string":
            type_enum = Type.STRING
        else:
            return self.add_error(f"Unsupported parameter type: {param_type}")
        # Verificar si el parámetro ya existe en la función actual
        if param_id in self.function_directory[self.current_scope].local_vars:
            return self.add_error(f"Parameter '{param_id}' already declared in function '{self.current_scope}'")
        # Crear y añadir el parámetro
        param_var = Variable(param_id, type_enum, self.current_scope)
        self.function_directory[self.current_scope].add_parameter(param_var)
        print(f"Added parameter '{param_id}' of type {type_enum} to function '{self.current_scope}'")
        return True

    def end_function_declaration(self):
        """Punto F5: Finalizar declaración de función"""
        if self.current_scope == "global":
            return self.add_error("Not inside a function declaration")
        # Store current scope before changing it
        func_name = self.current_scope
        # Pop current scope and return to previous (should be global)
        self.pop_scope()
        print(f"Ended function '{func_name}' declaration, returned to scope: {self.current_scope}")
        return True

    def check_variable(self, var_id):
        """Verifica si una variable existe y devuelve su tipo"""
        # Primero buscar en el ámbito local si no estamos en global
        if self.current_scope != "global" and var_id in self.function_directory[self.current_scope].local_vars:
            return self.function_directory[self.current_scope].local_vars[var_id].type
        # Luego buscar en el ámbito global
        if var_id in self.global_vars:
            return self.global_vars[var_id].type
        # Variable no encontrada
        self.add_error(f"Variable '{var_id}' not declared")
        return Type.ERROR

    def check_function(self, func_id):
        """Verifica si una función existe y devuelve información sobre ella"""
        if func_id in self.function_directory:
            return self.function_directory[func_id]
        self.add_error(f"Function '{func_id}' not declared")
        return None

    def check_assignment_compatibility(self, var_id, expr_type):
        """Punto A3: Verificar compatibilidad de tipos en asignación"""
        var_type = self.check_variable(var_id)
        if var_type == Type.ERROR:
            return False
        result_type = get_result_type(var_type, expr_type, Operation.ASSIGN)
        if result_type == Type.ERROR:
            return self.add_error(f"Incompatible types in assignment to '{var_id}': Cannot assign {expr_type} to {var_type}")
        return True

    def check_expression_compatibility(self, left_type, right_type, operation):
        """Verificar compatibilidad de tipos en expresiones"""
        result_type = get_result_type(left_type, right_type, operation)
        if result_type == Type.ERROR:
            self.add_error(f"Incompatible types in operation {operation}: {left_type} and {right_type}")
        return result_type

    def check_condition(self, expr_type):
        """Verificar que una expresión sea de tipo booleano para condiciones"""
        if expr_type != Type.BOOL:
            return self.add_error(f"Condition expression must be boolean, got {expr_type}")
        return True

    def print_function_directory(self):
        """Imprime el contenido del directorio de funciones"""
        print("\n===== FUNCTION DIRECTORY =====")
        for func_name, func in self.function_directory.items():
            print(f"{func}")
            print("  Parameters:")
            for param in func.parameters:
                print(f"    {param}")
            print("  Local Variables:")
            for var_name, var in func.local_vars.items():
                if var not in func.parameters:
                    print(f"    {var}")  
        print("\n===== GLOBAL VARIABLES =====")
        for var_name, var in self.global_vars.items():
            print(f"  {var}")
        
        if self.error_list:
            print("\n===== SEMANTIC ERRORS =====")
            for error in self.error_list:
                print(f"  {error}")
    
    def push_scope(self, new_scope):
        """Push a new scope onto the stack and set it as current"""
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope
        print(f"Pushed scope: {new_scope}, current scope stack: {self.scope_stack}")
        return True
    
    def pop_scope(self):
        """Pop the current scope from the stack and set the previous one as current"""
        if len(self.scope_stack) > 1:
            old_scope = self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
            print(f"Popped scope: {old_scope}, current scope is now: {self.current_scope}")
            return True
        else:
            self.add_error("Cannot pop global scope")
            return False