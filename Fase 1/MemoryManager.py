from semantic_cube import Type

class MemoryManager:
    def __init__(self):
        # Memory segments
        self.GLOBAL_INT_START = 1000
        self.GLOBAL_FLOAT_START = 3000
        self.LOCAL_INT_START = 5000
        self.LOCAL_FLOAT_START = 7000
        self.TEMP_INT_START = 9000
        self.TEMP_FLOAT_START = 11000
        self.CONST_INT_START = 13000
        self.CONST_FLOAT_START = 15000
        self.CONST_STRING_START = 17000
        
        # Current counters
        self.global_int_counter = 0
        self.global_float_counter = 0
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
        self.const_int_counter = 0
        self.const_float_counter = 0
        self.const_string_counter = 0
        
        # Constant table to avoid duplicates
        self.constants = {}
        
    def get_address(self, var_type, scope, is_temp=False):
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
        
        # For temporary variables
        if is_temp:
            if var_type == Type.INT:
                addr = self.TEMP_INT_START + self.temp_int_counter
                self.temp_int_counter += 1
                return addr
            elif var_type == Type.FLOAT:
                addr = self.TEMP_FLOAT_START + self.temp_float_counter
                self.temp_float_counter += 1
                return addr
        
        return -1  # Error case
    
    def get_constant_address(self, value):
        # Check if the constant already exists
        if value in self.constants:
            return self.constants[value]
        
        # Assign new address based on constant type
        if isinstance(value, int):
            addr = self.CONST_INT_START + self.const_int_counter
            self.const_int_counter += 1
        elif isinstance(value, float):
            addr = self.CONST_FLOAT_START + self.const_float_counter
            self.const_float_counter += 1
        elif isinstance(value, str):
            # For string constants
            addr = self.CONST_STRING_START + self.const_string_counter
            self.const_string_counter += 1
        else:
            return -1  # Unsupported constant type
        
        # Store in constants table
        self.constants[value] = addr
        return addr
    
    def reset_local_counters(self):
        # Reset local counters when exiting a function scope
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0