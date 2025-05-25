class VirtualMachine:
    def __init__(self, memory_manager, quadruples, function_directory):
        self.memory = memory_manager
        self.quadruples = quadruples
        self.function_directory = function_directory
        self.instruction_pointer = 0
        self.running = True
        
        # Establecer referencia del function directory en memory manager
        self.memory.function_directory = function_directory
        
        # Inicializar memoria
        self.memory.initialize_memory()
    
    def execute(self):
        """Ejecuta el programa desde el instruction pointer actual"""
        print("Starting Virtual Machine execution...")
        

        while self.running and self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            print(f"IP: {self.instruction_pointer} | Executing: {quad}")
            
            self.execute_instruction(quad)
            
            # Solo incrementar IP si no fue modificado por un salto
            if self.instruction_pointer == self.memory.instruction_pointer:
                self.instruction_pointer += 1
            else:
                self.instruction_pointer = self.memory.instruction_pointer
        
        print("Virtual Machine execution completed.")
    
    def execute_instruction(self, quad):
        """Ejecuta una instrucción individual"""
        operator = quad.operator
        left = quad.left_operand
        right = quad.right_operand
        result = quad.result
        print(f"Executing operator: {operator}")
        
        # Actualizar IP en memory manager
        self.memory.instruction_pointer = self.instruction_pointer
        
        if operator == '+':
            self.execute_arithmetic(left, right, result, lambda a, b: a + b)
        elif operator == '-':
            self.execute_arithmetic(left, right, result, lambda a, b: a - b)
        elif operator == '*':
            self.execute_arithmetic(left, right, result, lambda a, b: a * b)
        elif operator == '/':
            self.execute_arithmetic(left, right, result, lambda a, b: a / b if b != 0 else 0)
        elif operator == '>':
            self.execute_comparison(left, right, result, lambda a, b: a > b)
        elif operator == '<':
            self.execute_comparison(left, right, result, lambda a, b: a < b)
        elif operator == '!=':
            self.execute_comparison(left, right, result, lambda a, b: a != b)
        elif operator == '==':  # Agregar comparación de igualdad
            self.execute_comparison(left, right, result, lambda a, b: a == b)
        elif operator == '=':
            self.execute_assignment(left, result)
        elif operator == 'goto':
            self.execute_goto(result)
        elif operator == 'gotof':
            self.execute_gotof(left, result)
        elif operator == 'print':
            self.execute_print(left)
        elif operator == 'ERA':
            self.execute_era(left)
        elif operator == 'parámetro':
            self.execute_param(left, right)
        elif operator == 'GOSUB':
            self.execute_gosub(left)
        elif operator == 'ENDFUNC':
            self.execute_endfunc()
        elif operator == 'RETURN':
            self.execute_return(left)
        else:
            print(f"Warning: Unknown operator '{operator}'")
    
    def execute_arithmetic(self, left_addr, right_addr, result_addr, operation):
        """Ejecuta operaciones aritméticas - MEJORADO"""
        try:
            # Obtener valores (pueden ser literales o direcciones)
            if isinstance(left_addr, (int, float)):
                left_val = left_addr
            else:
                left_val = self.memory.get_value(left_addr)
                
            if isinstance(right_addr, (int, float)):
                right_val = right_addr
            else:
                right_val = self.memory.get_value(right_addr)
            
            # Realizar operación
            result_val = operation(left_val, right_val)
            
            # Guardar resultado
            self.memory.set_value(result_addr, result_val)
            
            print(f"  Arithmetic: {left_val} {operation.__name__} {right_val} = {result_val}")
            
        except Exception as e:
            print(f"  Arithmetic Error: {e}")
            # Asignar 0 como valor por defecto en caso de error
            self.memory.set_value(result_addr, 0)
    
    def execute_comparison(self, left_addr, right_addr, result_addr, comparison):
        """Ejecuta operaciones de comparación - MEJORADO"""
        try:
            # Obtener valores (pueden ser literales o direcciones)
            if isinstance(left_addr, (int, float)):
                left_val = left_addr
            else:
                left_val = self.memory.get_value(left_addr)
                
            if isinstance(right_addr, (int, float)):
                right_val = right_addr
            else:
                right_val = self.memory.get_value(right_addr)
            
            # Realizar comparación
            result_val = comparison(left_val, right_val)
            
            # Guardar resultado
            self.memory.set_value(result_addr, result_val)
            
            print(f"  Comparison: {left_val} {comparison.__name__} {right_val} = {result_val}")
            
        except Exception as e:
            print(f"  Comparison Error: {e}")
            # Asignar False como valor por defecto en caso de error
            self.memory.set_value(result_addr, False)
    
    def execute_assignment(self, source_addr, target_addr):
        """Ejecuta asignación - CORREGIDO"""
        print(f"Assignment: source={source_addr}, target={target_addr}")
        
        # Verificar si source_addr es un valor literal (constante)
        if isinstance(source_addr, (int, float)):
            # Es un valor literal - usar directamente
            value = source_addr
            print(f"  Literal value: {value}")
        else:
            # Es una dirección de memoria - obtener el valor
            try:
                value = self.memory.get_value(source_addr)
                print(f"  Retrieved from address {source_addr}: {value}")
            except Exception as e:
                print(f"  Error getting value from address {source_addr}: {e}")
                value = 0  # Valor por defecto
        
        # Asignar el valor a la dirección destino
        try:
            self.memory.set_value(target_addr, value)
            print(f"  Assignment successful: {value} -> address {target_addr}")
        except Exception as e:
            print(f"  Error setting value at address {target_addr}: {e}")
        
    def execute_goto(self, target_addr):
        """Ejecuta salto incondicional"""
        self.instruction_pointer = target_addr
        self.memory.instruction_pointer = target_addr
        print(f"  Goto: jumping to {target_addr}")
    
    def execute_gotof(self, condition_addr, target_addr):
        """Ejecuta salto condicional (goto if false)"""
        condition_val = self.memory.get_value(condition_addr)
        if not condition_val:  # Si es falso
            self.instruction_pointer = target_addr
            self.memory.instruction_pointer = target_addr
            print(f"  GotoF: condition false, jumping to {target_addr}")
        else:
            print(f"  GotoF: condition true, continuing")
    
    def execute_print(self, value_addr):
        """Ejecuta operación de impresión - CORREGIDO"""
        # Si es string literal, imprime directamente
        if isinstance(value_addr, str):
            print(f"OUTPUT: {value_addr}")
        # Si es dirección de memoria (int), imprime el valor almacenado
        elif isinstance(value_addr, int):
            try:
                value = self.memory.get_value(value_addr)
                print(f"OUTPUT: {value}")
            except Exception as e:
                print(f"OUTPUT ERROR: Could not retrieve value: {e}")
                print(f"OUTPUT: <undefined>")
        # Si es float, imprime el valor
        elif isinstance(value_addr, float):
            print(f"OUTPUT: {value_addr}")
        else:
            print(f"OUTPUT: {value_addr}")
    
    def execute_era(self, func_name):
        """Ejecuta ERA - reserva espacio para función"""
        print(f"  ERA: Reserving space for function '{func_name}'")
        self.memory.push_local_context()
    
    def execute_param(self, param_addr, param_id):
        """Ejecuta paso de parámetro"""
        param_value = self.memory.get_value(param_addr)
        print(f"  Parameter: {param_id} = {param_value}")
        # En una implementación completa, aquí asignarías el parámetro
        # a la dirección local correspondiente
    
    def execute_gosub(self, func_name):
        """Ejecuta llamada a función"""
        print(f"  GOSUB: Calling function '{func_name}'")
        
        # Guardar contexto actual
        return_addr = self.instruction_pointer + 1
        self.memory.push_execution_context(return_addr, func_name)
        
        # Saltar a la función
        if func_name in self.function_directory:
            func_start = self.function_directory[func_name].start_address
            if func_start is not None:
                self.instruction_pointer = func_start
                self.memory.instruction_pointer = func_start
            else:
                print(f"Error: Function '{func_name}' has no start address")
        else:
            print(f"Error: Function '{func_name}' not found")
    
    def execute_endfunc(self):
        """Ejecuta fin de función"""
        print("  ENDFUNC: Ending function")
        
        # Restaurar contexto
        context = self.memory.pop_execution_context()
        if context:
            self.instruction_pointer = context['return_address']
            self.memory.instruction_pointer = context['return_address']
            print(f"  Returning to address {context['return_address']}")
        
        # Limpiar contexto local
        self.memory.pop_local_context()
    
    def execute_return(self, value_addr):
        """Ejecuta retorno de función"""
        if value_addr is not None:
            return_value = self.memory.get_value(value_addr)
            print(f"  RETURN: Returning value {return_value}")
        else:
            print("  RETURN: Returning void")
        
        # Ejecutar el mismo proceso que ENDFUNC
        self.execute_endfunc()
    
    def debug_step(self):
        """Ejecuta una instrucción paso a paso para depuración"""
        if self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            print(f"\nDEBUG - Next instruction: {quad}")
            self.memory.print_memory_state()
            
            input("Press Enter to execute next instruction...")
            self.execute_instruction(quad)
            self.instruction_pointer += 1
            
            return True
        else:
            print("Program finished")
            return False