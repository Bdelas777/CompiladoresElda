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

    def backup_local_memory(self):
        """Hace backup de la memoria local actual"""
        return self.local_memory.copy()
    
    def restore_local_memory(self, backup):
        """Restaura la memoria local desde un backup"""
        self.local_memory = backup

class FunctionContext:
    """Contexto de ejecución de una función"""
    def __init__(self, function_name, return_address, local_memory_backup=None):
        self.function_name = function_name
        self.return_address = return_address
        self.local_memory_backup = local_memory_backup or {}
        self.parameters = {}
        self.local_vars = {}

class VirtualMachine:
    """Máquina Virtual para ejecutar cuádruplos"""
    def __init__(self, quadruples, constants_table, function_directory):
        self.quadruples = quadruples
        self.memory = ExecutionMemory()
        self.function_directory = function_directory
        self.instruction_pointer = 0
        self.call_stack = []
        self.current_function = "global"
        self.parameter_stack = []  # Para manejar parámetros de funciones
        self.function_contexts = []  # Stack de contextos de función
        
        # Inicializar tabla de constantes en memoria
        for value, address in constants_table.items():
            self.memory.set_value(address, value)
            
        print(f"Inicializando VM con {len(quadruples)} cuádruplos")
        print(f"Constantes inicializadas: {len(constants_table)}")
    
    def execute(self):
        """Ejecuta el programa completo"""
        print("=== INICIANDO EJECUCIÓN ===")
        self.instruction_pointer = 0
        
        try:
            while self.instruction_pointer < len(self.quadruples):
                quad = self.quadruples[self.instruction_pointer]
                print(f"IP: {self.instruction_pointer:3d} -> {quad}")
                
                if not self.execute_quadruple(quad):
                    break
                    
                self.instruction_pointer += 1
        except Exception as e:
            print(f"ERROR EN EJECUCIÓN: {e}")
            print(f"Cuádruplo actual: {self.quadruples[self.instruction_pointer] if self.instruction_pointer < len(self.quadruples) else 'Fuera de rango'}")
            raise
        
        print("=== EJECUCIÓN TERMINADA ===")
    
    def execute_quadruple(self, quad):
        """Ejecuta un cuádruplo individual"""
        op = quad.operator
        
        # Operaciones aritméticas
        if op == '+':
            return self._execute_arithmetic(quad, lambda a, b: a + b)
        elif op == '-':
            return self._execute_arithmetic(quad, lambda a, b: a - b)
        elif op == '*':
            return self._execute_arithmetic(quad, lambda a, b: a * b)
        elif op == '/':
            return self._execute_arithmetic(quad, lambda a, b: a / b if b != 0 else self._division_by_zero())
        
        # Operaciones de comparación
        elif op == '>':
            return self._execute_comparison(quad, lambda a, b: a > b)
        elif op == '<':
            return self._execute_comparison(quad, lambda a, b: a < b)
        elif op == '!=':
            return self._execute_comparison(quad, lambda a, b: a != b)
        elif op == '==':
            return self._execute_comparison(quad, lambda a, b: a == b)
        elif op == '>=':
            return self._execute_comparison(quad, lambda a, b: a >= b)
        elif op == '<=':
            return self._execute_comparison(quad, lambda a, b: a <= b)
        
        # Operaciones de control
        elif op == '=':
            return self._execute_assignment(quad)
        elif op == 'goto':
            return self._execute_goto(quad)
        elif op == 'gotof':
            return self._execute_gotof(quad)
        elif op == 'gotot':
            return self._execute_gotot(quad)
        
        # Operaciones de entrada/salida
        elif op == 'print':
            return self._execute_print(quad)
        elif op == 'read':
            return self._execute_read(quad)
        
        # Operaciones de función
        elif op == 'ERA':
            return self._execute_era(quad)
        elif op == 'parámetro' or op == 'param':
            return self._execute_param(quad)
        elif op == 'GOSUB':
            return self._execute_gosub(quad)
        elif op == 'ENDFUNC':
            return self._execute_endfunc(quad)
        elif op == 'RETURN':
            return self._execute_return(quad)
        
        # Operación de finalización
        elif op == 'END':
            print("Programa terminado normalmente")
            return False
        
        else:
            print(f"Operación no implementada: {op}")
            return True
    
    def _division_by_zero(self):
        """Maneja división por cero"""
        print("ERROR: División por cero detectada!")
        return 0
    
    def _execute_arithmetic(self, quad, operation):
        """Ejecuta operaciones aritméticas"""
        try:
            left_val = self.memory.get_value(quad.left_operand)
            right_val = self.memory.get_value(quad.right_operand)
            result = operation(left_val, right_val)
            self.memory.set_value(quad.result, result)
            print(f"  Aritmética: {left_val} {quad.operator} {right_val} = {result}")
            return True
        except Exception as e:
            print(f"  ERROR en operación aritmética: {e}")
            return False
    
    def _execute_comparison(self, quad, operation):
        """Ejecuta operaciones de comparación"""
        try:
            left_val = self.memory.get_value(quad.left_operand)
            right_val = self.memory.get_value(quad.right_operand)
            result = operation(left_val, right_val)
            # Convertir resultado booleano a entero (1 para true, 0 para false)
            self.memory.set_value(quad.result, 1 if result else 0)
            print(f"  Comparación: {left_val} {quad.operator} {right_val} = {result}")
            return True
        except Exception as e:
            print(f"  ERROR en comparación: {e}")
            return False
    
    def _execute_assignment(self, quad):
        """Ejecuta asignación"""
        try:
            value = self.memory.get_value(quad.left_operand)
            self.memory.set_value(quad.result, value)
            print(f"  Asignación: dirección[{quad.result}] = {value}")
            return True
        except Exception as e:
            print(f"  ERROR en asignación: {e}")
            return False
    
    def _execute_goto(self, quad):
        """Ejecuta salto incondicional"""
        try:
            target = quad.result
            if target < 0 or target >= len(self.quadruples):
                print(f"  ERROR: Dirección de salto inválida: {target}")
                return False
            self.instruction_pointer = target - 1  # -1 porque se incrementará
            print(f"  Salto incondicional a: {target}")
            return True
        except Exception as e:
            print(f"  ERROR en goto: {e}")
            return False
    
    def _execute_gotof(self, quad):
        """Ejecuta salto condicional (si falso)"""
        try:
            condition = self.memory.get_value(quad.left_operand)
            target = quad.result
            
            if not condition or condition == 0:
                if target < 0 or target >= len(self.quadruples):
                    print(f"  ERROR: Dirección de salto inválida: {target}")
                    return False
                self.instruction_pointer = target - 1
                print(f"  Salto condicional a: {target} (condición falsa: {condition})")
            else:
                print(f"  No hay salto (condición verdadera: {condition})")
            return True
        except Exception as e:
            print(f"  ERROR en gotof: {e}")
            return False
    
    def _execute_gotot(self, quad):
        """Ejecuta salto condicional (si verdadero)"""
        try:
            condition = self.memory.get_value(quad.left_operand)
            target = quad.result
            
            if condition and condition != 0:
                if target < 0 or target >= len(self.quadruples):
                    print(f"  ERROR: Dirección de salto inválida: {target}")
                    return False
                self.instruction_pointer = target - 1
                print(f"  Salto condicional a: {target} (condición verdadera: {condition})")
            else:
                print(f"  No hay salto (condición falsa: {condition})")
            return True
        except Exception as e:
            print(f"  ERROR en gotot: {e}")
            return False
    
    def _execute_print(self, quad):
        """Ejecuta impresión"""
        try:
            if isinstance(quad.left_operand, str):
                # Manejar cadenas literales
                if quad.left_operand.startswith('"') and quad.left_operand.endswith('"'):
                    output = quad.left_operand[1:-1]  # Quitar comillas
                else:
                    output = quad.left_operand
                print(f"OUTPUT: {output}")
            else:
                # Es una dirección de memoria
                value = self.memory.get_value(quad.left_operand)
                print(f"OUTPUT: {value}")
            return True
        except Exception as e:
            print(f"  ERROR en print: {e}")
            return False
    
    def _execute_read(self, quad):
        """Ejecuta lectura de entrada"""
        try:
            print("INPUT: ", end="")
            value = input()
            
            # Intentar convertir a número
            try:
                if '.' in value:
                    numeric_value = float(value)
                else:
                    numeric_value = int(value)
                self.memory.set_value(quad.result, numeric_value)
                print(f"  Read: '{value}' -> dirección[{quad.result}]")
            except ValueError:
                # Si no se puede convertir, almacenar como string (si se soporta)
                print(f"  ERROR: Valor no numérico: {value}")
                return False
            
            return True
        except Exception as e:
            print(f"  ERROR en read: {e}")
            return False
    
    def _execute_era(self, quad):
        """Reserva espacio para función (ERA)"""
        try:
            func_name = quad.left_operand
            print(f"  ERA: Reservando espacio para función '{func_name}'")
            
            # Limpiar el stack de parámetros para la nueva función
            self.parameter_stack.clear()
            
            # Preparar contexto para la nueva función
            self.current_function = func_name
            return True
        except Exception as e:
            print(f"  ERROR en ERA: {e}")
            return False
    
    def _execute_param(self, quad):
        """Pasa parámetro a función"""
        try:
            param_value = self.memory.get_value(quad.left_operand)
            param_number = quad.right_operand
            
            # Almacenar parámetro en el stack
            self.parameter_stack.append({
                'value': param_value,
                'param_number': param_number,
                'address': quad.left_operand
            })
            
            print(f"  Parámetro {param_number}: {param_value} (desde dirección {quad.left_operand})")
            return True
        except Exception as e:
            print(f"  ERROR en parámetro: {e}")
            return False
    
    def _execute_gosub(self, quad):
        """Llama a función"""
        try:
            func_name = quad.left_operand
            
            if func_name not in self.function_directory:
                print(f"  ERROR: Función '{func_name}' no encontrada")
                return False
            
            func_info = self.function_directory[func_name]
            
            if not hasattr(func_info, 'start_address'):
                print(f"  ERROR: Función '{func_name}' no tiene dirección de inicio")
                return False
            
            func_start = func_info.start_address
            
            # Crear contexto de función
            context = FunctionContext(
                func_name,
                self.instruction_pointer + 1,
                self.memory.backup_local_memory()
            )
            
            # Guardar contexto actual
            self.function_contexts.append(context)
            self.call_stack.append(self.instruction_pointer + 1)
            
            # Limpiar memoria local para la nueva función
            self.memory.clear_local_memory()
            
            # Asignar parámetros a memoria local si existen
            if hasattr(func_info, 'parameters') and func_info.parameters:
                for i, param in enumerate(func_info.parameters):
                    if i < len(self.parameter_stack):
                        param_value = self.parameter_stack[i]['value']
                        # Asignar parámetro a su dirección en memoria local
                        if hasattr(param, 'address'):
                            self.memory.set_value(param.address, param_value)
                            print(f"    Asignando parámetro {param.name}: {param_value} -> dirección {param.address}")
            
            # Saltar a la función
            self.instruction_pointer = func_start - 1
            print(f"  GOSUB: Llamando función '{func_name}' en dirección {func_start}")
            return True
            
        except Exception as e:
            print(f"  ERROR en GOSUB: {e}")
            return False
    
    def _execute_endfunc(self, quad):
        """Termina función"""
        try:
            if not self.call_stack:
                print("  ENDFUNC: No hay función para terminar")
                return True
            
            # Restaurar dirección de retorno
            return_address = self.call_stack.pop()
            self.instruction_pointer = return_address - 1
            
            # Restaurar contexto anterior
            if self.function_contexts:
                context = self.function_contexts.pop()
                self.memory.restore_local_memory(context.local_memory_backup)
                print(f"  ENDFUNC: Terminando función '{context.function_name}', retornando a dirección {return_address}")
            else:
                print(f"  ENDFUNC: Retornando a dirección {return_address}")
            
            # Limpiar stack de parámetros
            self.parameter_stack.clear()
            
            return True
        except Exception as e:
            print(f"  ERROR en ENDFUNC: {e}")
            return False
    
    def _execute_return(self, quad):
        """Retorna de función con valor"""
        try:
            if quad.left_operand is not None:
                return_value = self.memory.get_value(quad.left_operand)
                print(f"  RETURN: Retornando valor {return_value}")
                # Aquí se podría almacenar el valor de retorno en una ubicación específica
            else:
                print(f"  RETURN: Retorno sin valor")
            
            # Ejecutar lógica de ENDFUNC
            return self._execute_endfunc(quad)
        except Exception as e:
            print(f"  ERROR en RETURN: {e}")
            return False
    
    def print_memory_state(self):
        """Imprime el estado actual de la memoria"""
        print("\n=== ESTADO DE LA MEMORIA ===")
        
        if self.memory.global_memory:
            print("Memoria Global:")
            for addr, value in sorted(self.memory.global_memory.items()):
                print(f"  [{addr}]: {value}")
        
        if self.memory.local_memory:
            print("Memoria Local:")
            for addr, value in sorted(self.memory.local_memory.items()):
                print(f"  [{addr}]: {value}")
        
        if self.memory.temp_memory:
            print("Memoria Temporal:")
            for addr, value in sorted(self.memory.temp_memory.items()):
                print(f"  [{addr}]: {value}")
        
        if self.memory.constant_memory:
            print("Constantes:")
            for addr, value in sorted(self.memory.constant_memory.items()):
                print(f"  [{addr}]: {value}")
        
        if self.call_stack:
            print("Call Stack:")
            for i, addr in enumerate(self.call_stack):
                print(f"  [{i}]: {addr}")
        
        print("="*30)
    
    def print_execution_statistics(self):
        """Imprime estadísticas de ejecución"""
        print("\n=== ESTADÍSTICAS DE EJECUCIÓN ===")
        print(f"Cuádruplos ejecutados: {self.instruction_pointer}")
        print(f"Funciones en call stack: {len(self.call_stack)}")
        print(f"Contextos de función: {len(self.function_contexts)}")
        
        memory_usage = {
            'global': len(self.memory.global_memory),
            'local': len(self.memory.local_memory),
            'temp': len(self.memory.temp_memory),
            'constants': len(self.memory.constant_memory)
        }
        
        print("Uso de memoria:")
        for segment, count in memory_usage.items():
            print(f"  {segment}: {count} variables")
        print("="*35)