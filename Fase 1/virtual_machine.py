class VirtualMachine:
    def __init__(self, quadruples, constants_table, memory_manager):
        self.quadruples = quadruples
        self.constants_table = constants_table
        self.memory_manager = memory_manager
        
        # Memory segments for execution
        self.memory = {}
        
        # Instruction pointer
        self.ip = 0  # instruction pointer
        
        # Initialize memory segments
        self._initialize_memory()
        
        # Load constants into memory
        self._load_constants()
        
    def _initialize_memory(self):
        """Initialize all memory segments"""
        # Global integers: 1000-2999
        for i in range(1000, 3000):
            self.memory[i] = 0
            
        # Global floats: 3000-4999  
        for i in range(3000, 5000):
            self.memory[i] = 0.0
            
        # Local integers: 5000-6999
        for i in range(5000, 7000):
            self.memory[i] = 0
            
        # Local floats: 7000-8999
        for i in range(7000, 9000):
            self.memory[i] = 0.0
            
        # Temp integers: 9000-10999
        for i in range(9000, 11000):
            self.memory[i] = 0
            
        # Temp floats: 11000-12999
        for i in range(11000, 13000):
            self.memory[i] = 0.0
            
        # Constant integers: 13000-14999
        for i in range(13000, 15000):
            self.memory[i] = 0
            
        # Constant floats: 15000-16999
        for i in range(15000, 17000):
            self.memory[i] = 0.0
            
        # Constant strings: 17000-18999
        for i in range(17000, 19000):
            self.memory[i] = ""
    
    def _load_constants(self):
        """Load constants from constants table into memory"""
        for value, address in self.constants_table.items():
            self.memory[address] = value
    
    def get_value(self, address):
        """Get value from memory address"""
        if isinstance(address, (int, float, str)) and not isinstance(address, bool):
            # If it's already a literal value, return it
            if isinstance(address, str) and address.isdigit():
                return int(address)
            elif isinstance(address, str):
                try:
                    return float(address)
                except ValueError:
                    return address
            return address
        
        # If it's a memory address
        if address in self.memory:
            return self.memory[address]
        
        return 0  # Default value
    
    def set_value(self, address, value):
        """Set value at memory address"""
        if address in self.memory:
            self.memory[address] = value
        else:
            print(f"Warning: Trying to set value at invalid address {address}")
    
    def execute(self):
        """Main execution loop"""
        print("Starting Virtual Machine execution...")
        print("=" * 50)
        
        while self.ip < len(self.quadruples):
            quad = self.quadruples[self.ip]
            print(f"IP: {self.ip} | Executing: {quad}")
            
            # Execute current quadruple
            self._execute_quadruple(quad)
            
            # Move to next instruction (unless it's a jump)
            self.ip += 1
        
        print("=" * 50)
        print("Virtual Machine execution completed.")
    
    def _execute_quadruple(self, quad):
        """Execute a single quadruple"""
        op = quad.operator
        left = quad.left_operand
        right = quad.right_operand
        result = quad.result
        
        if op == '+':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            self.set_value(result, left_val + right_val)
            
        elif op == '-':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            self.set_value(result, left_val - right_val)
            
        elif op == '*':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            self.set_value(result, left_val * right_val)
            
        elif op == '/':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            if right_val == 0:
                print("Runtime Error: Division by zero")
                return
            self.set_value(result, left_val / right_val)
            
        elif op == '>':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            self.set_value(result, 1 if left_val > right_val else 0)
            
        elif op == '<':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            self.set_value(result, 1 if left_val < right_val else 0)
            
        elif op == '!=':
            left_val = self.get_value(left)
            right_val = self.get_value(right)
            self.set_value(result, 1 if left_val != right_val else 0)
            
        elif op == '=':
            # Assignment
            value = self.get_value(left)
            self.set_value(result, value)
            
        elif op == 'goto':
            # Unconditional jump
            self.ip = result - 1  # -1 because ip will be incremented
            
        elif op == 'gotof':
            # Conditional jump (jump if false)
            condition = self.get_value(left)
            if not condition or condition == 0:
                self.ip = result - 1  # -1 because ip will be incremented
                
        elif op == 'print':
            # Print operation
            if isinstance(left, str) and left.startswith('"') and left.endswith('"'):
                # String literal
                print(left[1:-1])  # Remove quotes
            else:
                # Variable or expression result
                value = self.get_value(left)
                print(value)
                
        elif op == 'call':
            # Function call - for now just print
            print(f"Calling function: {left}")
            
        elif op == 'param':
            # Parameter passing - for now just print
            value = self.get_value(left)
            print(f"Parameter: {value}")
            
        else:
            print(f"Unknown operation: {op}")
    
    def print_memory_state(self):
        """Print current state of memory (non-zero values only)"""
        print("\n=== MEMORY STATE ===")
        
        # Global variables
        print("Global Integers (1000-2999):")
        for addr in range(1000, 3000):
            if self.memory[addr] != 0:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        print("Global Floats (3000-4999):")
        for addr in range(3000, 5000):
            if self.memory[addr] != 0.0:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        # Local variables
        print("Local Integers (5000-6999):")
        for addr in range(5000, 7000):
            if self.memory[addr] != 0:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        print("Local Floats (7000-8999):")
        for addr in range(7000, 9000):
            if self.memory[addr] != 0.0:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        # Temporary variables
        print("Temp Integers (9000-10999):")
        for addr in range(9000, 11000):
            if self.memory[addr] != 0:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        print("Temp Floats (11000-12999):")
        for addr in range(11000, 13000):
            if self.memory[addr] != 0.0:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        # Constants
        print("Constants:")
        for addr in range(13000, 19000):
            if addr in self.memory and self.memory[addr] not in [0, 0.0, ""]:
                print(f"  [{addr}]: {self.memory[addr]}")
        
        print("===================\n")