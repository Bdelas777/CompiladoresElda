from semantic_cube import Type

class MemoryManager:
    def __init__(self):
        # Memory segments ranges
        self.GLOBAL_INT_START = 1000
        self.GLOBAL_FLOAT_START = 3000
        self.LOCAL_INT_START = 5000
        self.LOCAL_FLOAT_START = 7000
        self.TEMP_INT_START = 9000
        self.TEMP_FLOAT_START = 11000
        self.TEMP_BOOL_START = 13000
        self.CONST_INT_START = 15000
        self.CONST_FLOAT_START = 17000
        
        # Memory segment sizes (para controlar límites)
        self.SEGMENT_SIZE = 2000
        
        # Current counters for address generation
        self.global_int_counter = 0
        self.global_float_counter = 0
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
        self.temp_bool_counter = 0
        self.const_int_counter = 0
        self.const_float_counter = 0
        
        # Constant table to avoid duplicates
        self.constants = {}
        
        # NUEVAS ESTRUCTURAS PARA LA MÁQUINA VIRTUAL
        
        # Memory spaces - almacenan los valores reales
        self.global_memory = {}     # {address: value}
        self.local_memory_stack = [] # Stack de memorias locales para funciones
        self.temp_memory = {}       # {address: value} para temporales
        self.constant_memory = {}   # {address: value} para constantes
        
        # Execution stack para manejo de funciones
        self.execution_stack = []   # Stack de contextos de ejecución
        
        # Instruction pointer
        self.instruction_pointer = 0
        
        # Function directory reference (se establecerá desde afuera)
        self.function_directory = None
        
    def get_address(self, var_type, scope, is_temp=False):
        """Genera direcciones virtuales para variables"""
        if is_temp:
            if var_type == Type.INT:
                addr = self.TEMP_INT_START + self.temp_int_counter
                self.temp_int_counter += 1
                return addr
            elif var_type == Type.FLOAT:
                addr = self.TEMP_FLOAT_START + self.temp_float_counter
                self.temp_float_counter += 1
                return addr
            elif var_type == Type.BOOL:
                addr = self.TEMP_BOOL_START + self.temp_bool_counter
                self.temp_bool_counter += 1
                return addr
        
        if scope == "global":
            if var_type == Type.INT:
                addr = self.GLOBAL_INT_START + self.global_int_counter
                self.global_int_counter += 1
                return addr
            elif var_type == Type.FLOAT:
                addr = self.GLOBAL_FLOAT_START + self.global_float_counter
                self.global_float_counter += 1
                return addr
        else:  # Local scope
            if var_type == Type.INT:
                addr = self.LOCAL_INT_START + self.local_int_counter
                self.local_int_counter += 1
                return addr
            elif var_type == Type.FLOAT:
                addr = self.LOCAL_FLOAT_START + self.local_float_counter
                self.local_float_counter += 1
                return addr
        
        return -1  # Error case
    
    def get_constant_address(self, value):
        """Genera direcciones para constantes"""
        if value in self.constants:
            return self.constants[value]
        
        if isinstance(value, int):
            addr = self.CONST_INT_START + self.const_int_counter
            self.const_int_counter += 1
        elif isinstance(value, float):
            addr = self.CONST_FLOAT_START + self.const_float_counter
            self.const_float_counter += 1
        else:
            return -1
        
        self.constants[value] = addr
        # Almacenar el valor en memoria de constantes
        self.constant_memory[addr] = value
        return addr
    
    def reset_local_counters(self):
        """Reinicia contadores locales al salir de una función"""
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
        self.temp_bool_counter = 0
    
    # NUEVOS MÉTODOS PARA LA MÁQUINA VIRTUAL
    
    def get_memory_segment(self, address):
        """Determina a qué segmento de memoria pertenece una dirección"""
        if self.GLOBAL_INT_START <= address < self.GLOBAL_INT_START + self.SEGMENT_SIZE:
            return "global_int"
        elif self.GLOBAL_FLOAT_START <= address < self.GLOBAL_FLOAT_START + self.SEGMENT_SIZE:
            return "global_float"
        elif self.LOCAL_INT_START <= address < self.LOCAL_INT_START + self.SEGMENT_SIZE:
            return "local_int"
        elif self.LOCAL_FLOAT_START <= address < self.LOCAL_FLOAT_START + self.SEGMENT_SIZE:
            return "local_float"
        elif self.TEMP_INT_START <= address < self.TEMP_INT_START + self.SEGMENT_SIZE:
            return "temp_int"
        elif self.TEMP_FLOAT_START <= address < self.TEMP_FLOAT_START + self.SEGMENT_SIZE:
            return "temp_float"
        elif self.TEMP_BOOL_START <= address < self.TEMP_BOOL_START + self.SEGMENT_SIZE:
            return "temp_bool"
        elif self.CONST_INT_START <= address < self.CONST_INT_START + self.SEGMENT_SIZE:
            return "const_int"
        elif self.CONST_FLOAT_START <= address < self.CONST_FLOAT_START + self.SEGMENT_SIZE:
            return "const_float"
        else:
            return "unknown"
    
    def get_value(self, address):
        """Obtiene el valor almacenado en una dirección de memoria"""
        segment = self.get_memory_segment(address)
        
        if segment.startswith("global"):
            return self.global_memory.get(address, 0)
        elif segment.startswith("local"):
            if self.local_memory_stack:
                current_local = self.local_memory_stack[-1]
                return current_local.get(address, 0)
            return 0
        elif segment.startswith("temp"):
            return self.temp_memory.get(address, 0)
        elif segment.startswith("const"):
            return self.constant_memory.get(address, 0)
        else:
            raise RuntimeError(f"Invalid memory address: {address}")
    
    def set_value(self, address, value):
        """Establece un valor en una dirección de memoria"""
        segment = self.get_memory_segment(address)
        
        if segment.startswith("global"):
            self.global_memory[address] = value
        elif segment.startswith("local"):
            if not self.local_memory_stack:
                self.local_memory_stack.append({})
            current_local = self.local_memory_stack[-1]
            current_local[address] = value
        elif segment.startswith("temp"):
            self.temp_memory[address] = value
        elif segment.startswith("const"):
            # Las constantes normalmente no se modifican, pero permitimos por flexibilidad
            self.constant_memory[address] = value
        else:
            raise RuntimeError(f"Invalid memory address for assignment: {address}")
    
    def push_local_context(self):
        """Crea un nuevo contexto local para una función"""
        self.local_memory_stack.append({})
    
    def pop_local_context(self):
        """Elimina el contexto local actual"""
        if self.local_memory_stack:
            return self.local_memory_stack.pop()
        return {}
    
    def push_execution_context(self, return_address, function_name):
        """Guarda el contexto de ejecución actual"""
        context = {
            'return_address': return_address,
            'function_name': function_name,
            'instruction_pointer': self.instruction_pointer
        }
        self.execution_stack.append(context)
    
    def pop_execution_context(self):
        """Restaura el contexto de ejecución anterior"""
        if self.execution_stack:
            return self.execution_stack.pop()
        return None
    
    def clear_temp_memory(self):
        """Limpia la memoria de temporales"""
        self.temp_memory.clear()
    
    def print_memory_state(self):
        """Método de depuración para ver el estado de la memoria"""
        print("\n===== MEMORY STATE =====")
        print("Global Memory:")
        for addr, val in sorted(self.global_memory.items()):
            print(f"  {addr}: {val}")
        
        print("Local Memory Stack:")
        for i, local_mem in enumerate(self.local_memory_stack):
            print(f"  Level {i}:")
            for addr, val in sorted(local_mem.items()):
                print(f"    {addr}: {val}")
        
        print("Temp Memory:")
        for addr, val in sorted(self.temp_memory.items()):
            print(f"  {addr}: {val}")
        
        print("Constant Memory:")
        for addr, val in sorted(self.constant_memory.items()):
            print(f"  {addr}: {val}")
        
        print("Execution Stack:")
        for i, context in enumerate(self.execution_stack):
            print(f"  Level {i}: {context}")
        print("========================\n")
    
    def initialize_memory(self):
        """Inicializa la memoria con valores por defecto"""
        # Inicializar memoria global con ceros
        for addr in range(self.GLOBAL_INT_START, self.GLOBAL_INT_START + self.global_int_counter):
            if addr not in self.global_memory:
                self.global_memory[addr] = 0
        
        for addr in range(self.GLOBAL_FLOAT_START, self.GLOBAL_FLOAT_START + self.global_float_counter):
            if addr not in self.global_memory:
                self.global_memory[addr] = 0.0