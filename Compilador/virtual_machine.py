from semantic_cube import Type
from MemoryManager import MemoryManager

class ExecutionMemory:
    """Mapa de memoria para la ejecución con segmentación por tipos"""
    def __init__(self):
        self.global_int_memory = {}     
        self.global_float_memory = {}    
        self.local_int_memory = {}       
        self.local_float_memory = {}    
        self.temp_int_memory = {}       
        self.temp_float_memory = {}    
        self.temp_bool_memory = {}       
        self.const_int_memory = {}      
        self.const_float_memory = {}   
        self.call_stack = []
        self.current_context = None
        
    def get_value(self, address):
        """Obtiene el valor almacenado en una dirección virtual"""
        # Globales enteros
        if 5000 <= address < 8000:
            return self.global_int_memory.get(address, 0)
        # Globales flotantes
        elif 8000 <= address < 11000:
            return self.global_float_memory.get(address, 0.0)
        # Locales enteros
        elif 11000 <= address < 13000:
            return self.local_int_memory.get(address, 0)
        # Locales flotantes
        elif 13000 <= address < 15000:
            return self.local_float_memory.get(address, 0.0)
        # Temporales enteros
        elif 15000 <= address < 17000:
            return self.temp_int_memory.get(address, 0)
        # Temporales flotantes
        elif 17000 <= address < 19000:
            return self.temp_float_memory.get(address, 0.0)
        # Temporales booleanos
        elif 19000 <= address < 20000:
            return self.temp_bool_memory.get(address, False)
        # Constantes enteras
        elif 20000 <= address < 20500:
            return self.const_int_memory.get(address, 0)
        # Constantes flotantes
        elif address >= 20500:
            return self.const_float_memory.get(address, 0.0)
        else:
            raise ValueError(f"Invalid memory address: {address}")
    
    def set_value(self, address, value):
        """Almacena un valor en una dirección virtual"""
        # Globales enteros
        if 5000 <= address < 8000:
            self.global_int_memory[address] = int(value) if not isinstance(value, bool) else value
        # Globales flotantes
        elif 8000 <= address < 11000:
            self.global_float_memory[address] = float(value)
        # Locales enteros
        elif 11000 <= address < 13000:
            self.local_int_memory[address] = int(value) if not isinstance(value, bool) else value
        # Locales flotantes
        elif 13000 <= address < 15000:
            self.local_float_memory[address] = float(value)
        # Temporales enteros
        elif 15000 <= address < 17000:
            self.temp_int_memory[address] = int(value) if not isinstance(value, bool) else value
        # Temporales flotantes
        elif 17000 <= address < 19000:
            self.temp_float_memory[address] = float(value)
        # Temporales booleanos
        elif 19000 <= address < 20000:
            self.temp_bool_memory[address] = bool(value)
        # Constantes enteras
        elif 20000 <= address < 20500:
            self.const_int_memory[address] = int(value) if not isinstance(value, bool) else value
        # Constantes flotantes
        elif address >= 20500:
            self.const_float_memory[address] = float(value)
        else:
            raise ValueError(f"Invalid memory address: {address}")
    
    def clear_local_memory(self):
        """Limpia la memoria local al terminar una función"""
        self.local_int_memory.clear()
        self.local_float_memory.clear()
    
    def clear_temp_memory(self):
        """Limpia la memoria temporal"""
        self.temp_int_memory.clear()
        self.temp_float_memory.clear()
        self.temp_bool_memory.clear()

    def save_local_context(self):
        """Guarda el contexto local actual"""
        return {
            'local_int': self.local_int_memory.copy(),
            'local_float': self.local_float_memory.copy()
        }
    
    def restore_local_context(self, context):
        """Restaura un contexto local"""
        self.local_int_memory = context['local_int']
        self.local_float_memory = context['local_float']

class VirtualMachine:
    """Máquina Virtual para ejecutar cuádruplos con memoria segmentada"""
    def __init__(self, quadruples, constants_table, function_directory):
        self.quadruples = quadruples
        self.memory = ExecutionMemory()
        self.function_directory = function_directory
        self.instruction_pointer = 0
        self.call_stack = []
        self.param_stack = []
        self.current_function = None
        self.memory_context_stack = []     
        self.program_outputs = []
        for value, address in constants_table.items():
            self.memory.set_value(address, value)
    
    def execute(self):
        """Ejecuta el programa completo"""
        print("=== INICIANDO EJECUCIÓN ===")
        self.instruction_pointer = 0
        self.program_outputs = []  
        while self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            print(f"IP: {self.instruction_pointer} -> Ejecutando: {quad}")
            if not self.execute_quadruple(quad):
                break   
            self.instruction_pointer += 1
        print("=== EJECUCIÓN TERMINADA ===")
    
    def _execute_end(self, quad):
        """Termina la ejecución del programa"""
        print("  END: Terminando programa")
        return False

    def execute_quadruple(self, quad):
        """Ejecuta un cuádruplo individual"""
        op = quad.operator
        
        if op == '+':
            return self._execute_arithmetic(quad, lambda a, b: a + b)
        elif op == '-':
            return self._execute_arithmetic(quad, lambda a, b: a - b)
        elif op == '*':
            return self._execute_arithmetic(quad, lambda a, b: a * b)
        elif op == '/':
            return self._execute_arithmetic(quad, lambda a, b: a / b if b != 0 else 0)
        elif op == '>':
            return self._execute_comparison(quad, lambda a, b: a > b)
        elif op == '<':
            return self._execute_comparison(quad, lambda a, b: a < b)
        elif op == '!=':
            return self._execute_comparison(quad, lambda a, b: a != b)
        elif op == '>=':
            return self._execute_comparison(quad, lambda a, b: a >= b)
        elif op == '=':
            return self._execute_assignment(quad)
        elif op == 'goto':
            return self._execute_goto(quad)
        elif op == 'gotof':
            return self._execute_gotof(quad)
        elif op == 'print':
            return self._execute_print(quad)
        elif op == 'ERA':
            return self._execute_era(quad)
        elif op == 'parámetro':
            return self._execute_param(quad)
        elif op == 'GOSUB':
            return self._execute_gosub(quad)
        elif op == 'ENDFUNC':
            return self._execute_endfunc(quad)
        elif op == 'RETURN':
            return self._execute_return(quad)
        elif op == 'END':
            return self._execute_end(quad)
        else:
            print(f"Operación no implementada: {op}")
            return True
    
    def _execute_arithmetic(self, quad, operation):
        """Ejecuta operaciones aritméticas"""
        left_val = self.memory.get_value(quad.left_operand)
        right_val = self.memory.get_value(quad.right_operand)
        result = operation(left_val, right_val)
        self.memory.set_value(quad.result, result)
        print(f"  Aritmética: {left_val} {quad.operator} {right_val} = {result}")
        return True
    
    def _execute_comparison(self, quad, operation):
        """Ejecuta operaciones de comparación"""
        left_val = self.memory.get_value(quad.left_operand)
        right_val = self.memory.get_value(quad.right_operand)
        result = operation(left_val, right_val)
        self.memory.set_value(quad.result, result)
        print(f"  Comparación: {left_val} {quad.operator} {right_val} = {result}")
        return True
    
    def _execute_logical(self, quad, operation):
        """Ejecuta operaciones lógicas"""
        left_val = bool(self.memory.get_value(quad.left_operand))
        right_val = bool(self.memory.get_value(quad.right_operand))
        result = operation(left_val, right_val)
        self.memory.set_value(quad.result, result)
        print(f"  Lógica: {left_val} {quad.operator} {right_val} = {result}")
        return True
    
    def _execute_assignment(self, quad):
        """Ejecuta asignación"""
        value = self.memory.get_value(quad.left_operand)
        self.memory.set_value(quad.result, value)
        print(f"  Asignación: direccion[{quad.result}] = {value}")
        return True
    
    def _execute_goto(self, quad):
        """Ejecuta salto incondicional"""
        self.instruction_pointer = quad.result - 1 
        print(f"  Salto a: {quad.result}")
        return True
    
    def _execute_gotof(self, quad):
        """Ejecuta salto condicional (si falso)"""
        condition = self.memory.get_value(quad.left_operand)
        if not condition:
            self.instruction_pointer = quad.result - 1
            print(f"  Salto condicional a: {quad.result} (condición falsa)")
        else:
            print(f"  No hay salto (condición verdadera)")
        return True
    
    def _execute_print(self, quad):
        """Ejecuta impresión"""
        if isinstance(quad.left_operand, str):
            output_value = quad.left_operand
            print(f"OUTPUT: {output_value}")
            self.program_outputs.append(output_value)
        else:
            value = self.memory.get_value(quad.left_operand)
            print(f"OUTPUT: {value}")
            self.program_outputs.append(str(value))
        return True
    
    def _execute_era(self, quad):
        """Reserva espacio para función (ERA)"""
        func_name = quad.left_operand
        print(f"  ERA: Reservando espacio para función '{func_name}'")
        
        self.param_stack = []
        self.current_function = func_name
        
        return True
    
    def _execute_param(self, quad):
        """Pasa parámetro a función"""
        param_value = self.memory.get_value(quad.left_operand)
        self.param_stack.append(param_value)
        print(f"  Parámetro: {param_value} -> posición {len(self.param_stack)}")
        return True
    
    def _execute_gosub(self, quad):
        """Llama a función"""
        func_name = quad.left_operand
        return_address = quad.result  
        if func_name in self.function_directory:
            func_info = self.function_directory[func_name]
            func_start = func_info.start_address
            if hasattr(self, 'current_function') and self.current_function:
                context = self.memory.save_local_context()
                self.memory_context_stack.append(context)          
            self.memory.clear_local_memory()
            if hasattr(func_info, 'local_vars') and self.param_stack:
                param_vars = []
                for var_name, var_info in func_info.local_vars.items():
                    param_vars.append((var_name, var_info.address))
                param_vars.sort(key=lambda x: x[1])
                for i, param_value in enumerate(self.param_stack):
                    if i < len(param_vars):
                        param_address = param_vars[i][1]
                        self.memory.set_value(param_address, param_value)
                        print(f"    Asignando parámetro {param_vars[i][0]} (addr: {param_address}) = {param_value}")           
            context = {
                'return_address': self.instruction_pointer + 1,
                'return_value_address': return_address,
                'function_name': func_name
            }
            self.call_stack.append(context)
            
            self.instruction_pointer = func_start - 1
            print(f"  GOSUB: Llamando función '{func_name}' en dirección {func_start}")
            if return_address:
                print(f"    Valor de retorno se guardará en dirección: {return_address}")
        return True
    
    def _execute_endfunc(self, quad):
        """Termina función"""
        if self.call_stack:
            context = self.call_stack.pop()
            self.instruction_pointer = context['return_address'] - 1
            print(f"  ENDFUNC: Retornando a dirección {context['return_address']}")
            if self.memory_context_stack:
                previous_context = self.memory_context_stack.pop()
                self.memory.restore_local_context(previous_context)
            else:
                self.memory.clear_local_memory()
            self.param_stack = []
            self.current_function = None
        return True
    
    def _execute_return(self, quad):
        """Retorna de función con valor"""
        if quad.left_operand is not None:
            return_value = self.memory.get_value(quad.left_operand)
            print(f"  RETURN: Retornando valor {return_value}")
            if self.call_stack:
                context = self.call_stack[-1] 
                if context.get('return_value_address'):
                    self.memory.set_value(context['return_value_address'], return_value)
                    print(f"    Valor guardado en dirección temporal: {context['return_value_address']}")
        else:
            print(f"  RETURN: Retorno sin valor")
        return self._execute_endfunc(quad)
    
    def print_program_outputs(self):
        """Imprime solo los outputs del programa de manera limpia"""
        print("\n=== SALIDA DEL PROGRAMA ===")
        for i, output in enumerate(self.program_outputs, 1):
            print(f"{output}")
            if i < len(self.program_outputs) and not self.program_outputs[i].replace('.', '').replace('-', '').isdigit():
                print()
        print("\n" + "="*27)
    
    def get_program_outputs(self):
        """Retorna la lista de outputs del programa"""
        return self.program_outputs
    
    def print_memory_state(self):
        """Imprime el estado actual de la memoria segmentada"""
        print("\n=== ESTADO DE LA MEMORIA SEGMENTADA ===")
        
        print("Memoria Global Enteros (5000-7999):")
        for addr, value in sorted(self.memory.global_int_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Memoria Global Flotantes (8000-10999):")
        for addr, value in sorted(self.memory.global_float_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Memoria Local Enteros (11000-12999):")
        for addr, value in sorted(self.memory.local_int_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Memoria Local Flotantes (13000-14999):")
        for addr, value in sorted(self.memory.local_float_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Memoria Temporal Enteros (15000-16999):")
        for addr, value in sorted(self.memory.temp_int_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Memoria Temporal Flotantes (17000-18999):")
        for addr, value in sorted(self.memory.temp_float_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Memoria Temporal Booleanos (19000-19999):")
        for addr, value in sorted(self.memory.temp_bool_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Constantes Enteras (20000-20499):")
        for addr, value in sorted(self.memory.const_int_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("Constantes Flotantes (20500+):")
        for addr, value in sorted(self.memory.const_float_memory.items()):
            print(f"  [{addr}]: {value}")
            
        print("="*40)