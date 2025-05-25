from semantic_cube import Type

class MemoryManager:
    def __init__(self):
        # Memory segments
        self.GLOBAL_INT_START = 5000
        self.GLOBAL_FLOAT_START = 8000
        self.LOCAL_INT_START = 11000
        self.LOCAL_FLOAT_START = 13000
        self.TEMP_INT_START = 15000
        self.TEMP_FLOAT_START = 17000
        self.TEMP_BOOL_START = 19000
        self.CONST_INT_START = 20000
        self.CONST_FLOAT_START = 20500
        
        # Current counters
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
        else:
            return -1  # Unsupported constant type
        
        # Store in constants table
        self.constants[value] = addr
        return addr
    
    def reset_local_counters(self):
        # Reset local counters when exiting a function scope
        self.local_int_counter = 0
        self.local_float_counter = 0

class MemoryTableGenerator:
    def __init__(self, semantic_analyzer):
        self.semantic = semantic_analyzer
        
    def generate_all_tables(self):
        """Genera todas las tablas de memoria"""
        print("\n" + "="*60)
        print("MEMORY ALLOCATION TABLES")
        print("="*60)
        
        self._generate_global_table()
        self._generate_local_tables()
        self._generate_constants_table()
        self._generate_function_directory()
        
    def _generate_global_table(self):
        """Genera la tabla de variables globales"""
        print("\n📊 TABLA DE VARIABLES GLOBALES")
        print("┌" + "─"*15 + "┬" + "─"*10 + "┬" + "─"*10 + "┐")
        print("│ Variable       │ Address  │ Type     │")
        print("├" + "─"*15 + "┼" + "─"*10 + "┼" + "─"*10 + "┤")
        
        if not self.semantic.global_vars:
            print("│ (No global variables)                 │")
        else:
            for var_name, var in self.semantic.global_vars.items():
                type_str = "int" if var.type == Type.INT else "float"
                print(f"│ {var_name:<14} │ {var.address:<8} │ {type_str:<8} │")
        
        print("└" + "─"*15 + "┴" + "─"*10 + "┴" + "─"*10 + "┘")
    
    def _generate_local_tables(self):
        """Genera las tablas de variables locales por función"""
        for func_name, func in self.semantic.function_directory.items():
            if func.local_vars:
                print(f"\n📊 TABLA DE VARIABLES LOCALES - FUNCIÓN: {func_name.upper()}")
                print("┌" + "─"*15 + "┬" + "─"*10 + "┬" + "─"*10 + "┐")
                print("│ Variable       │ Address  │ Type     │")
                print("├" + "─"*15 + "┼" + "─"*10 + "┼" + "─"*10 + "┤")
                
                for var_name, var in func.local_vars.items():
                    type_str = "int" if var.type == Type.INT else "float"
                    print(f"│ {var_name:<14} │ {var.address:<8} │ {type_str:<8} │")
                
                print("└" + "─"*15 + "┴" + "─"*10 + "┴" + "─"*10 + "┘")
    
    def _generate_constants_table(self):
        """Genera la tabla de constantes"""
        print(f"\n📊 TABLA DE CONSTANTES")
        print("┌" + "─"*15 + "┬" + "─"*10 + "┬" + "─"*10 + "┐")
        print("│ Value          │ Address  │ Type     │")
        print("├" + "─"*15 + "┼" + "─"*10 + "┼" + "─"*10 + "┤")
        
        if not self.semantic.memory_manager.constants:
            print("│ (No constants used)                   │")
        else:
            for value, address in self.semantic.memory_manager.constants.items():
                type_str = "int" if isinstance(value, int) else "float"
                print(f"│ {str(value):<14} │ {address:<8} │ {type_str:<8} │")
        
        print("└" + "─"*15 + "┴" + "─"*10 + "┴" + "─"*10 + "┘")
    
    def _generate_function_directory(self):
        """Genera el directorio de funciones"""
        print(f"\n📊 DIRECTORIO DE FUNCIONES")
        print("┌" + "─"*15 + "┬" + "─"*12 + "┬" + "─"*8 + "┬" + "─"*8 + "┬" + "─"*8 + "┐")
        print("│ Function       │ Start Addr   │ Params │ Vars   │ Temps  │")
        print("├" + "─"*15 + "┼" + "─"*12 + "┼" + "─"*8 + "┼" + "─"*8 + "┼" + "─"*8 + "┤")
        
        for func_name, func in self.semantic.function_directory.items():
            start_addr = getattr(func, 'start_address', 'N/A')
            params = len(func.parameters)
            vars_count = func.var_count
            temps = 0  # Se calcularía durante la generación de cuádruplos
            
            print(f"│ {func_name:<14} │ {str(start_addr):<12} │ {params:<6} │ {vars_count:<6} │ {temps:<6} │")
        
        print("└" + "─"*15 + "┴" + "─"*12 + "┴" + "─"*8 + "┴" + "─"*8 + "┴" + "─"*8 + "┘")
    
    def generate_simple_tables(self):
        """Genera tablas en formato simple como en tu ejemplo"""
        print("\n" + "="*40)
        print("MEMORY TABLES (Simple Format)")
        print("="*40)
        
        # Tabla de globales
        if self.semantic.global_vars:
            print("\n📋 globales")
            for var_name, var in self.semantic.global_vars.items():
                type_char = 'i' if var.type == Type.INT else 'f'
                print(f"{var_name:<8} {var.address:<8} {type_char}")
        
        # Tablas de locales por función
        for func_name, func in self.semantic.function_directory.items():
            if func.local_vars:
                print(f"\n📋 locales a {func_name.upper()}")
                for var_name, var in func.local_vars.items():
                    type_char = 'i' if var.type == Type.INT else 'f'
                    print(f"{var_name:<8} {var.address:<8} {type_char}")
        
        # Tabla de constantes
        if self.semantic.memory_manager.constants:
            print(f"\n📋 CTE's")
            for value, address in self.semantic.memory_manager.constants.items():
                type_char = 'i' if isinstance(value, int) else 'f'
                print(f"{str(value):<8} {address:<8} {type_char}")

# Función de prueba para tablas de memoria
def test_memory_tables():
    """Función para probar la generación de tablas con datos de ejemplo"""
    from semantic_analyzer import SemanticAnalyzer
    
    # Crear analizador semántico
    semantic = SemanticAnalyzer()
    
    # Simular programa con variables globales
    semantic.program_start("test_program")
    
    # Agregar variables globales
    semantic.start_var_declaration()
    semantic.add_id_to_temp_list("i")
    semantic.add_id_to_temp_list("j")
    semantic.set_current_type("int")
    semantic.add_vars_to_table()
    
    semantic.start_var_declaration()
    semantic.add_id_to_temp_list("f")
    semantic.add_id_to_temp_list("dos")
    semantic.set_current_type("float")
    semantic.add_vars_to_table()
    
    # Declarar función UNO
    semantic.declare_function("UNO")
    semantic.add_parameter("a", "int")
    semantic.add_parameter("b", "float")
    semantic.end_function_declaration()
    
    # Declarar función DOS
    semantic.declare_function("DOS")
    semantic.add_parameter("a", "int")
    
    # Variables locales en DOS
    semantic.start_var_declaration()
    semantic.add_id_to_temp_list("i")
    semantic.add_id_to_temp_list("j")
    semantic.set_current_type("float")
    semantic.add_vars_to_table()
    
    semantic.end_function_declaration()
    
    # Declarar main
    semantic.declare_main()
    semantic.end_function_declaration()
    
    # Agregar algunas constantes
    semantic.memory_manager.get_constant_address(0)
    semantic.memory_manager.get_constant_address(2)
    semantic.memory_manager.get_constant_address(1)
    semantic.memory_manager.get_constant_address(3.14)
    semantic.memory_manager.get_constant_address(3)
    semantic.memory_manager.get_constant_address(1.5)
    
    # Generar tablas
    table_gen = MemoryTableGenerator(semantic)
    table_gen.generate_all_tables()
    print("\n" + "="*60)
    table_gen.generate_simple_tables()

if __name__ == "__main__":
    test_memory_tables()