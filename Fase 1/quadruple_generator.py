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
        self.main_goto_index = None 
        
    def new_temp(self, temp_type):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        temp_address = self.semantic.memory_manager.get_address(temp_type, self.semantic.current_scope, is_temp=True)
        return temp_address
        
    def generate_arithmetic_quad(self):
        """Versión corregida que maneja mejor las operaciones encadenadas"""
        if not self.POper or len(self.PilaO) < 2 or not self.PTypes:
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
    def get_operand_address(self, operand):
        if isinstance(operand, int):
            return operand
        if self.semantic.current_scope != "global" and operand in self.semantic.function_directory[self.semantic.current_scope].local_vars:
            return self.semantic.function_directory[self.semantic.current_scope].local_vars[operand].address
        if operand in self.semantic.global_vars:
            return self.semantic.global_vars[operand].address
        try:
            if '.' in str(operand):
                value = float(operand)
            else:
                value = int(operand)
            if value not in self.constants_table:
                address = self.semantic.memory_manager.get_constant_address(value)
                self.constants_table[value] = address
            return self.constants_table[value]
        except ValueError:
            pass
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
        target_address = self.get_operand_address(target_id)
        expr_address = self.get_operand_address(expression_result)
        quad = Quadruple('=', expr_address, None, target_address)
        self.Quads.append(quad)
        self.quad_counter += 1
        return True
        
    def generate_print_quad(self, value):
        if isinstance(value, int):
            quad = Quadruple('print', value, None, None)
        else:
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
        for var_name, var in self.semantic.global_vars.items():
            if var.address == address:
                return f"{var_name} (global)"
        if self.semantic.current_scope != "global":
            for var_name, var in self.semantic.function_directory[self.semantic.current_scope].local_vars.items():
                if var.address == address:
                    return f"{var_name} (local in {self.semantic.current_scope})"
        for value, addr in self.constants_table.items():
            if addr == address:
                return f"constant({value})"
        if isinstance(address, str) and address.startswith('t'):
            return f"temp {address}"
        
        return f"addr:{address}"
    
    def _get_quad_explanation(self, quad):
        """Generate a human-readable explanation of the quadruple."""
        op = quad.operator
        left = quad.left_operand
        right = quad.right_operand
        result = quad.result
        left_name = self.get_address_content(left) if left is not None else None
        right_name = self.get_address_content(right) if right is not None else None
        result_name = self.get_address_content(result) if result is not None else None
        if op in ['+', '-', '*', '/']:
            op_map = {'+': 'add', '-': 'subtract', '*': 'multiply', '/': 'divide'}
            return f"{op_map[op]} {left_name} and {right_name}, store result in {result_name}"
        elif op == '=':
            return f"assign value of {left_name} to {result_name}"
        elif op in ['>', '<', '!=']:
            op_map = {'>': 'greater than', '<': 'less than', '!=': 'not equal to'}
            return f"compare if {left_name} is {op_map[op]} {right_name}, store boolean result in {result_name}"
        elif op == 'goto':
            return f"jump to quadruple {result}"
        elif op == 'gotof':
            return f"if {left_name} is false, jump to quadruple {result}"
        elif op == 'call':
            return f"call function {left}"
        elif op == 'param':
            return f"pass parameter {left_name}"
        elif op == 'return':
            return f"return value {left_name}"
        elif op == 'print':
            return f"print value {left_name}"
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
        self._print_function_info()
        current_function = None
        for i, quad in enumerate(self.Quads):
            function_name = self._get_function_at_quad(i)
            if function_name and function_name != current_function:
                current_function = function_name
                print(f"\n{'='*20} FUNCTION: {function_name.upper()} {'='*20}")
                print(f"Starting at quadruple {i}")
                print("-" * 70)
            print(f"{i}: {quad}")
            explanation = self._get_quad_explanation(quad)
            print(f"      {explanation}")
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
        # Obtener información de la función
        func_info = self.semantic.function_directory.get(func_name)
        if func_info and func_info.return_type != Type.VOID:
            # Si la función retorna un valor, crear una variable temporal para almacenarlo
            temp_result = self.new_temp(func_info.return_type)
            quad = Quadruple('GOSUB', func_name, None, None)
            # Guardar el resultado temporal en la pila para que pueda ser usado
            self.PilaO.append(temp_result)
            self.PTypes.append(func_info.return_type)
        else:
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
    
    def generate_end_quad(self):
        """Genera cuádruplo END para terminar el programa"""
        quad = Quadruple('END', None, None, None)
        self.Quads.append(quad)
        self.quad_counter += 1
        return self.quad_counter - 1
    
    def generate_assignment_from_function_quad(self, target_var, function_result_var):
        """Genera asignación desde el resultado de una función"""
        target_address = self.get_operand_address(target_var)
        # El resultado de la función se almacena en una variable especial
        result_address = self.get_operand_address(function_result_var)
        quad = Quadruple('=', result_address, None, target_address)
        self.Quads.append(quad)
        self.quad_counter += 1
        return True

    def generate_return_quad(self, return_value=None):
        """Genera cuádruplo RETURN - ya existe pero asegurar que esté correcto"""
        if return_value:
            quad = Quadruple('RETURN', return_value, None, None)
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
    
    def get_execution_data(self):
        """Retorna los datos necesarios para la máquina virtual"""
        return {
            'quadruples': self.Quads,
            'constants_table': self.constants_table,
            'function_directory': self.semantic.function_directory
        }