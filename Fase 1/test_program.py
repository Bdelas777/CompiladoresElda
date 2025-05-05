from yacc import parse_program
import logging

# Test code 1: Simple function with parameters
test_code1 = """
program Test1;
var
  global1, global2 : int;
  global3 : float;

void testFunc(param1: int, param2: float) {
    var
      local1 : int;
      local2 : float;
    
    local1 = param1 + 10;
    local2 = param2 * 2.5;
    
    print(local1, local2);
}

main 
{
    global1 = 5;
    global2 = 10;
    global3 = 15.5;
    
    testFunc(global1, global3);
    testFunc(global2, 20.0);
}
end
"""

# Test code 2: Function with parameter mismatch (error case)
test_code2 = """
program Test2;
var
  x, y : int;
  z : float;

void calculate(a: int, b: int, c: float) {
    var
      result : float;
    
    result = a + b * c;
    print(result);
}

main 
{
    x = 5;
    y = 10;
    z = 2.5;
    
    calculate(x, y, z);   // Correct
    calculate(x, z);      // Error: Wrong number of parameters
    calculate(z, y, x);   // Error: Type mismatch
}
end
"""

# Test code 3: Multiple functions
test_code3 = """
program Test3;
var
  value : int;
  result : float;

void increment(x: int) {
    value = x + 1;
}

void multiply(a: float, b: float) {
    result = a * b;
}

main 
{
    value = 10;
    result = 0.0;
    
    increment(value);
    multiply(result, 2.5);
    
    print("Value:", value);
    print("Result:", result);
}
end
"""

def run_test(code, test_name):
    print(f"\n{'='*50}")
    print(f"Running test: {test_name}")
    print(f"{'='*50}")
    
    result, errors = parse_program(code)
    
    print(f"\nParse result: {'Success' if result else 'Failed'}")
    if errors:
        print(f"\nFound {len(errors)} semantic errors:")
        for i, error in enumerate(errors):
            print(f"  {i+1}. {error}")
    else:
        print("\nNo semantic errors found.")
    
    print(f"{'='*50}\n")
    
    return result, errors

if __name__ == "__main__":
    print("\nTesting BabyDuck parameter handling\n")
    
    run_test(test_code1, "Function with correct parameters")
    run_test(test_code2, "Function with parameter errors")
    run_test(test_code3, "Multiple functions with parameters")