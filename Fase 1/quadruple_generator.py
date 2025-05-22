from semantic_cube import Type, Operation, get_result_type

class Quadruple:
    def __init__(self, operator, left_operand, right_operand, result):
        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand
        self.result = result

    def __str__(self):
        return f"({self.operator}, {self.left_operand}, {self.right_operand}, {self.result})"

class QuadrupleGenerator:
    def __init__(self, semantic_analyzer):
        self.semantic = semantic_analyzer
        self.PilaO = []  
        self.POper = []  
        self.PTypes = []  
        self.PJumps = []  
        self.Quads = []  
        self.temp_counter = 0
        self.quad_counter = 0
        self.false_bottom = '('  
        self.constants_table = {}  
        self.param_counter = 0
        
    def new_temp(self, temp_type):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        # Assign virtual address to temporary variable
        temp_address = self.semantic.memory_manager.get_address(temp_type, self.semantic.current_scope, is_temp=True)
        return temp_address
        
    def generate_arithmetic_quad(self):
        if not self.POper or not self.PilaO or not self.PTypes:
            return False
            
        operator = self.POper[-1]
        if operator in ['+', '-', '*', '/', '>', '<', '!=']:
            right_operand = self.PilaO.pop()
            right_type = self.PTypes.pop()
            left_operand = self.PilaO.pop()
            left_type = self.PTypes.pop()
            operator = self.POper.pop()
            
            operation = None
            if operator == '+': operation = Operation.PLUS
            elif operator == '-': operation = Operation.MINUS
            elif operator == '*': operation = Operation.MULTIPLY
            elif operator == '/': operation = Operation.DIVIDE
            elif operator == '>': operation = Operation.GREATER
            elif operator == '<': operation = Operation.LESS
            elif operator == '!=': operation = Operation.NOT_EQUAL
            
            result_type = get_result_type(left_type, right_type, operation)
            
            if result_type != Type.ERROR:
                result = self.new_temp(result_type)
                
                # Convert operands to addresses if they're not already
                left_address = self.get_operand_address(left_operand)
                right_address = self.get_operand_address(right_operand)
                
                quad = Quadruple(operator, left_address, right_address, result)
                self.Quads.append(quad)
                self.quad_counter += 1
                self.PilaO.append(result)
                self.PTypes.append(result_type)
                return True
            else:
                self.semantic.add_error(f"Type mismatch: {left_type} {operator} {right_type}")
                return False
        return False
    
    def get_operand_address(self, operand):
        # If operand is already an address (number)
        if isinstance(operand, int):
            return operand
            
        # If operand is a variable name
        if self.semantic.current_scope != "global" and operand in self.semantic.function_directory[self.semantic.current_scope].local_vars:
            return self.semantic.function_directory[self.semantic.current_scope].local_vars[operand].address
        if operand in self.semantic.global_vars:
            return self.semantic.global_vars[operand].address
            
        # If operand is a constant
        try:
            # Try to convert to int or float
            if '.' in operand:
                value = float(operand)
            else:
                value = int(operand)
            # Get or create address for constant
            if value not in self.constants_table:
                address = self.semantic.memory_manager.get_constant_address(value)
                self.constants_table[value] = address
            return self.constants_table[value]
        except ValueError:
            # For string constants
            if operand.startswith('"') and operand.endswith('"'):
                value = operand[1:-1]  # Remove quotes
                if value not in self.constants_table:
                    address = self.semantic.memory_manager.get_constant_address(value)
                    self.constants_table[value] = address
                return self.constants_table[value]
        
        # Return -1 if not found
        return -1
       
    def process_operator(self, operator):
        self.POper.append(operator)
        
    def process_operand(self, operand_id, operand_type):
        self.PilaO.append(operand_id)
        self.PTypes.append(operand_type)
        
    def check_top_operation(self, operators_list):
        if self.POper and self.POper[-1] in operators_list:
            return self.generate_arithmetic_quad()
        return False
        
    def push_false_bottom(self):
        self.POper.append(self.false_bottom)
        
    def pop_false_bottom(self):
        if self.POper and self.POper[-1] == self.false_bottom:
            self.POper.pop()
            return True
        return False
        
    def generate_assignment_quad(self, target_id, expression_result):
        # Get the address of the target variable
        target_address = self.get_operand_address(target_id)
        # Get the address of the expression result
        expr_address = self.get_operand_address(expression_result)
        
        quad = Quadruple('=', expr_address, None, target_address)
        self.Quads.append(quad)
        self.quad_counter += 1
        return True
        
    def generate_print_quad(self, value):
        quad = Quadruple('print', value, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return True
        
    def generate_goto_quad(self):
        quad = Quadruple('goto', None, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1
            
    def generate_gotof_quad(self, condition):
        # Get the address of the condition
        condition_address = self.get_operand_address(condition)
        
        quad = Quadruple('gotof', condition_address, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1
        
    def fill_quad(self, quad_index, jump_target):
        if 0 <= quad_index < len(self.Quads):
            self.Quads[quad_index].result = jump_target
            return True
        return False
            
    def fill_from_jumps(self, jump_target):
        if self.PJumps:
            quad_index = self.PJumps.pop()
            return self.fill_quad(quad_index, jump_target)
        return False
        
    def get_address_content(self, address):
        """Try to find the variable or constant name associated with an address."""
        # Check global variables
        for var_name, var in self.semantic.global_vars.items():
            if var.address == address:
                return f"{var_name} (global)"
        
        # Check local variables in current scope
        if self.semantic.current_scope != "global":
            for var_name, var in self.semantic.function_directory[self.semantic.current_scope].local_vars.items():
                if var.address == address:
                    return f"{var_name} (local in {self.semantic.current_scope})"
        
        # Check constants (reverse lookup)
        for value, addr in self.constants_table.items():
            if addr == address:
                return f"constant({value})"
        
        # For temporaries, we can't easily find the original name
        if isinstance(address, str) and address.startswith('t'):
            return f"temp {address}"
        
        return f"addr:{address}"
    
    def _get_quad_explanation(self, quad):
        """Generate a human-readable explanation of the quadruple."""
        op = quad.operator
        left = quad.left_operand
        right = quad.right_operand
        result = quad.result
        
        # Get human-readable names for addresses
        left_name = self.get_address_content(left) if left is not None else None
        right_name = self.get_address_content(right) if right is not None else None
        result_name = self.get_address_content(result) if result is not None else None
        
        # Basic arithmetic operations
        if op in ['+', '-', '*', '/']:
            op_map = {'+': 'add', '-': 'subtract', '*': 'multiply', '/': 'divide'}
            return f"{op_map[op]} {left_name} and {right_name}, store result in {result_name}"
        
        # Assignment
        elif op == '=':
            return f"assign value of {left_name} to {result_name}"
        
        # Comparison operations
        elif op in ['>', '<', '!=']:
            op_map = {'>': 'greater than', '<': 'less than', '!=': 'not equal to'}
            return f"compare if {left_name} is {op_map[op]} {right_name}, store result in {result_name}"
        
        # Jumps
        elif op == 'goto':
            return f"jump to quadruple {result}"
        elif op == 'gotof':
            return f"if {left_name} is false, jump to quadruple {result}"
        
        # Function operations
        elif op == 'call':
            return f"call function {left}"
        elif op == 'param':
            return f"pass parameter {left_name}"
        elif op == 'return':
            return f"return value {left_name}"
        
        # Print
        elif op == 'print':
            if isinstance(left, str) and (left.startswith('"') and left.endswith('"')):
                # It's a string literal
                return f"print string \"{left}\""
            else:
                return f"print value {left_name}"
        
        # Default case
        else:
            if right is None and result is None:
                return f"perform operation {op} with operand {left_name}"
            elif right is None:
                return f"perform operation {op} with operand {left_name}, result in {result_name}"
            else:
                return f"perform operation {op} with operands {left_name}, {right_name}, result in {result_name}"
                
    def print_quads(self):
        print("\n===== QUADRUPLES WITH MEMORY ADDRESSES =====")
        print("INDEX: (OPERATOR, LEFT_OPERAND, RIGHT_OPERAND, RESULT)")
        print("      EXPLANATION")
        print("-" * 70)
        
        # Imprimir información de funciones primero
        self._print_function_info()
        
        current_function = None
        
        for i, quad in enumerate(self.Quads):
            # Detectar inicio de función
            function_name = self._get_function_at_quad(i)
            if function_name and function_name != current_function:
                current_function = function_name
                print(f"\n{'='*20} FUNCTION: {function_name.upper()} {'='*20}")
                print(f"Starting at quadruple {i}")
                print("-" * 70)
            
            print(f"{i}: {quad}")
            
            # Generate explanation based on operator
            explanation = self._get_quad_explanation(quad)
            print(f"      {explanation}")
            
            # Detectar fin de función
            if quad.operator == 'ENDFUNC':
                print(f"{'='*20} END OF {current_function.upper()} {'='*20}")
                current_function = None
            
            print("-" * 70)
        
    def _print_function_info(self):
        """Imprime información sobre las funciones y sus direcciones de inicio"""
        print("\n===== FUNCTION DIRECTORY =====")
        for func_name, func_info in self.semantic.function_directory.items():
            start_addr = getattr(func_info, 'start_address', 'Not set')
            print(f"Function: {func_name} - Start Address: {start_addr}")
        print("-" * 70)
    
    def _get_function_at_quad(self, quad_index):
        """Determina qué función está ejecutándose en el cuádruplo dado"""
        # Buscar en el directorio de funciones cuál tiene esta dirección de inicio
        for func_name, func_info in self.semantic.function_directory.items():
            if hasattr(func_info, 'start_address') and func_info.start_address == quad_index:
                return func_name
        return None
       
    def generate_era_quad(self, func_name):
        """Genera cuádruplo ERA para reservar espacio de función"""
        quad = Quadruple('ERA', func_name, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1

    def generate_param_quad(self, param_address, param_number):
        """Genera cuádruplo para pasar parámetro"""
        quad = Quadruple('parámetro', param_address, f'par{param_number}', None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1

    def generate_gosub_quad(self, func_name):
        """Genera cuádruplo GOSUB para llamar función"""
        quad = Quadruple('GOSUB', func_name, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1

    def generate_endfunc_quad(self):
        """Genera cuádruplo ENDFUNC para terminar función"""
        quad = Quadruple('ENDFUNC', None, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1

    def generate_return_quad(self, return_value=None):
        """Genera cuádruplo RETURN"""
        if return_value:
            return_address = self.get_operand_address(return_value)
            quad = Quadruple('RETURN', return_address, None, None)
        else:
            quad = Quadruple('RETURN', None, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1

    def save_function_start(self, func_name):
        """Guarda la dirección de inicio de una función"""
        if func_name in self.semantic.function_directory:
            self.semantic.function_directory[func_name].start_address = self.quad_counter
        return self.quad_counter
    
    def reset_param_counter(self):
        """Reinicia el contador de parámetros para una nueva llamada a función"""
        self.param_counter = 0

    def increment_param_counter(self):
        """Incrementa y retorna el contador de parámetros"""
        self.param_counter += 1
        return self.param_counter
    
    def get_current_quad_index(self):
        """Retorna el índice actual de cuádruplos (próximo a generar)"""
        return len(self.Quads)
