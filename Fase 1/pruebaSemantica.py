# test_babyduck.py - Sistema de pruebas para el compilador BabyDuck
import sys
import datetime
import traceback
from io import StringIO
import logging

# Configurar logging
logging.basicConfig(
    filename='prueba.log',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'  # 'w' para sobrescribir el archivo en cada ejecución
)

# Importar el lexer y parser
from yacc import parse_program

# Test code 1: Simple function with parameters
test_code1 = """
program pelos;

var
    x, y : float;

void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];

main {
    a : float;
    a = 1 + 2;
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
    logging.info(f"\n{'='*50}")
    logging.info(f"Running test: {test_name}")
    logging.info(f"{'='*50}\n")
    
    logging.info("Código:")
    logging.info(code.strip())
    logging.info("\n")
    
    try:
        result, errors = parse_program(code)
        
        logging.info(f"Parse result: {'Success' if result else 'Failed'}")
        if errors:
            logging.info(f"\nFound {len(errors)} semantic errors:")
            for i, error in enumerate(errors):
                logging.info(f"  {i+1}. {error}")
        else:
            logging.info("\nNo semantic errors found.")
    except Exception as e:
        logging.info(f"Error durante la prueba:")
        logging.info(traceback.format_exc())
    
    logging.info(f"{'-'*80}\n")

def run_tests():
    test_cases = [
        ("P-FUNC-01", test_code1, "Function with correct parameters"),
        # ("P-FUNC-02", test_code2, "Function with parameter errors"),
        # ("P-FUNC-03", test_code3, "Multiple functions with parameters")
    ]
    
    original_stdout = sys.stdout
    
    logging.info(f"== INICIO DE PRUEBAS - {datetime.datetime.now()} ==\n")
    
    for code, input_text, description in test_cases:
        run_test(input_text, f"{code} - {description}")
    
    logging.info(f"\n== FIN DE PRUEBAS - {datetime.datetime.now()} ==\n")
    
    print("Pruebas completadas. Resultados guardados en prueba.log")

if __name__ == "__main__":
    print("\nTesting BabyDuck parameter handling\n")
    run_tests()