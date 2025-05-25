from semantic_cube import Type
from MemoryManager import MemoryManager

class ExecutionMemory:
    """Mapa de memoria para la ejecución"""
    def __init__(self):
        # Memoria física para cada segmento
        self.global_memory = {}      # 5000-10999: Variables globales
        self.local_memory = {}       # 11000-14999: Variables locales
        self.temp_memory = {}        # 15000-19999: Variables temporales
        self.constant_memory = {}    # 20000+: Constantes
        
        # Stack para llamadas a funciones
        self.call_stack = []
        self.current_context = None
        
    def get_value(self, address):
        """Obtiene el valor almacenado en una dirección virtual"""
        if 5000 <= address < 11000:
            return self.global_memory.get(address, 0)
        elif 11000 <= address < 15000:
            return self.local_memory.get(address, 0)
        elif 15000 <= address < 20000:
            return self.temp_memory.get(address, 0)
        elif address >= 20000:
            return self.constant_memory.get(address, 0)
        else:
            raise ValueError(f"Invalid memory address: {address}")
    
    def set_value(self, address, value):
        """Almacena un valor en una dirección virtual"""
        if 5000 <= address < 11000:
            self.global_memory[address] = value
        elif 11000 <= address < 15000:
            self.local_memory[address] = value
        elif 15000 <= address < 20000:
            self.temp_memory[address] = value
        elif address >= 20000:
            self.constant_memory[address] = value
        else:
            raise ValueError(f"Invalid memory address: {address}")
    
    def clear_local_memory(self):
        """Limpia la memoria local al terminar una función"""
        self.local_memory.clear()
    
    def clear_temp_memory(self):
        """Limpia la memoria temporal"""
        self.temp_memory.clear()

class VirtualMachine:
    """Máquina Virtual para ejecutar cuádruplos"""
    def __init__(self, quadruples, constants_table, function_directory):
        self.quadruples = quadruples
        self.memory = ExecutionMemory()
        self.function_directory = function_directory
        self.instruction_pointer = 0
        self.call_stack = []
        
        # Inicializar tabla de constantes en memoria
        for value, address in constants_table.items():
            self.memory.set_value(address, value)
    
    def execute(self):
        """Ejecuta el programa completo"""
        print("=== INICIANDO EJECUCIÓN ===")
        self.instruction_pointer = 0
        
        while self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            print(f"IP: {self.instruction_pointer} -> Ejecutando: {quad}")
            
            if not self.execute_quadruple(quad):
                break
                
            self.instruction_pointer += 1
        
        print("=== EJECUCIÓN TERMINADA ===")
    
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
        self.memory.set_value(quad.result, 1 if result else 0)
        print(f"  Comparación: {left_val} {quad.operator} {right_val} = {result}")
        return True
    
    def _execute_assignment(self, quad):
        """Ejecuta asignación"""
        value = self.memory.get_value(quad.left_operand)
        self.memory.set_value(quad.result, value)
        print(f"  Asignación: direccion[{quad.result}] = {value}")
        return True
    
    def _execute_goto(self, quad):
        """Ejecuta salto incondicional"""
        self.instruction_pointer = quad.result - 1  # -1 porque se incrementará
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
            # Es una cadena literal
            print(f"OUTPUT: {quad.left_operand}")
        else:
            # Es una dirección de memoria
            value = self.memory.get_value(quad.left_operand)
            print(f"OUTPUT: {value}")
        return True
    
    def _execute_era(self, quad):
        """Reserva espacio para función (ERA)"""
        func_name = quad.left_operand
        print(f"  ERA: Reservando espacio para función '{func_name}'")
        # Limpiar memoria local para nueva función
        self.memory.clear_local_memory()
        return True
    
    def _execute_param(self, quad):
        """Pasa parámetro a función"""
        param_value = self.memory.get_value(quad.left_operand)
        param_address = quad.right_operand  # Dirección del parámetro
        print(f"  Parámetro: {param_value} -> {param_address}")
        # Aquí se asignaría el valor al parámetro en la función
        return True
    
    def _execute_gosub(self, quad):
        """Llama a función"""
        func_name = quad.left_operand
        if func_name in self.function_directory:
            func_start = self.function_directory[func_name].start_address
            # Guardar contexto actual
            self.call_stack.append(self.instruction_pointer + 1)
            self.instruction_pointer = func_start - 1
            print(f"  GOSUB: Llamando función '{func_name}' en dirección {func_start}")
        return True
    
    def _execute_endfunc(self, quad):
        """Termina función"""
        if self.call_stack:
            self.instruction_pointer = self.call_stack.pop() - 1
            print(f"  ENDFUNC: Retornando a dirección {self.instruction_pointer + 1}")
            self.memory.clear_local_memory()
        return True
    
    def _execute_return(self, quad):
        """Retorna de función con valor"""
        if quad.left_operand:
            return_value = self.memory.get_value(quad.left_operand)
            print(f"  RETURN: Retornando valor {return_value}")
        else:
            print(f"  RETURN: Retorno sin valor")
        return self._execute_endfunc(quad)
    
    def print_memory_state(self):
        """Imprime el estado actual de la memoria"""
        print("\n=== ESTADO DE LA MEMORIA ===")
        print("Memoria Global:")
        for addr, value in sorted(self.memory.global_memory.items()):
            print(f"  [{addr}]: {value}")
        print("Memoria Local:")
        for addr, value in sorted(self.memory.local_memory.items()):
            print(f"  [{addr}]: {value}")
        print("Memoria Temporal:")
        for addr, value in sorted(self.memory.temp_memory.items()):
            print(f"  [{addr}]: {value}")
        print("Constantes:")
        for addr, value in sorted(self.memory.constant_memory.items()):
            print(f"  [{addr}]: {value}")
        print("="*30)