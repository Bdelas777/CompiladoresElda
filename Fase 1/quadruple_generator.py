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
        
    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
        
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
                result = self.new_temp()
                quad = Quadruple(operator, left_operand, right_operand, result)
                self.Quads.append(quad)
                self.quad_counter += 1
                self.PilaO.append(result)
                self.PTypes.append(result_type)
                return True
            else:
                self.semantic.add_error(f"Type mismatch: {left_type} {operator} {right_type}")
                return False
        return False
        
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
        quad = Quadruple('=', expression_result, None, target_id)
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
        self.PJumps.append(self.quad_counter)
        self.quad_counter += 1
        return self.quad_counter - 1
        
    def generate_gotof_quad(self, condition):
        quad = Quadruple('gotof', condition, None, None)
        self.Quads.append(quad)
        self.PJumps.append(self.quad_counter)
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
