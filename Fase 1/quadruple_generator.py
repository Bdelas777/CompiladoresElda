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
        self.PilaO = []  # Operands stack
        self.POper = []  # Operators stack
        self.PTypes = []  # Types stack
        self.PJumps = []  # Jumps stack
        self.Quads = []  # Quadruples queue
        self.temp_counter = 0
        self.quad_counter = 0
        self.false_bottom = '('  # False bottom marker
        self.constants_table = {}  # To track constants
        
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
        
    def print_quads(self):
        print("\n===== QUADRUPLES =====")
        for i, quad in enumerate(self.Quads):
            print(f"{i}: {quad}")
