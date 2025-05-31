from semantic_cube import Type

class MemoryManager:
    def __init__(self):
        # Definimos la memoria por segmentos dependiendo de que vamos a usar
        self.GLOBAL_INT_START = 5000
        self.GLOBAL_FLOAT_START = 8000
        self.LOCAL_INT_START = 11000
        self.LOCAL_FLOAT_START = 13000
        self.TEMP_INT_START = 15000
        self.TEMP_FLOAT_START = 17000
        self.TEMP_BOOL_START = 19000
        self.CONST_INT_START = 20000
        self.CONST_FLOAT_START = 20500
        
        self.global_int_counter = 0
        self.global_float_counter = 0
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
        self.temp_bool_counter = 0
        self.const_int_counter = 0
        self.const_float_counter = 0
        self.constants = {}
    
    # Funcion para obtener la dirección de memoria de una variable
    def get_address(self, var_type, scope, is_temp=False):
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
        elif scope == "global":
            if var_type == Type.INT:
                addr = self.GLOBAL_INT_START + self.global_int_counter
                self.global_int_counter += 1
                return addr
            elif var_type == Type.FLOAT:
                addr = self.GLOBAL_FLOAT_START + self.global_float_counter
                self.global_float_counter += 1
                return addr
        else:  
            if var_type == Type.INT:
                addr = self.LOCAL_INT_START + self.local_int_counter
                self.local_int_counter += 1
                return addr
            elif var_type == Type.FLOAT:
                addr = self.LOCAL_FLOAT_START + self.local_float_counter
                self.local_float_counter += 1
                return addr
        
        return -1  
    
    # Funcion para obtener la dirección de memoria de una constante
    def get_constant_address(self, value):
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
        return addr
    
    # Resetear los contadores locales y temporales
    def reset_local_counters(self):
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
        self.temp_bool_counter = 0  
