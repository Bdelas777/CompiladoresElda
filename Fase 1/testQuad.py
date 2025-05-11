#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from datetime import datetime
import logging
import io
from contextlib import redirect_stdout

# Assuming your parser implementation is in a file called 'parser.py'
# Make sure this file is in the same directory or in your Python path
try:
    from yacc import parse_program
except ImportError:
    print("Error: Could not import parse_program from parser.py")
    print("Make sure parser.py is in the same directory or in your Python path")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("compiler_tests.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("compiler_test")

# Test programs
TEST_PROGRAMS = {
    "arithmetic": """
program operaciones_basicas;
var
    a, b, c, resultado, resultado2 : int;
    resultado3 : float;

main {
    a = 5;
    b = 10;
    c = 2;
    
    resultado = a + b * c;
    print("Resultado 1: ", resultado);
    
    resultado2 = (a + b) * c;
    print("Resultado 2: ", resultado2);
    
    resultado3 = a - b / c;
    print("Resultado 3: ", resultado3);
}
end
""",
    
    "if_else": """
program control_if;
var
    x, y, max : int;
main {
    x = 15;
    y = 7;
    
    if (x > y) {
        max = x;
        print("El mayor es x: ", max);
    } else {
        max = y;
        print("El mayor es y: ", max);
    };
    
    if (x < 10) {
        print("x es menor que 10");
    } else {
        print("x es mayor o igual que 10");
    };
}
end
""",
    
    "while_loop": """
program ciclo_while;
var
    contador, suma : int;
main {
    contador = 1;
    suma = 0;
    
    while (contador < 5) do {
        suma = suma + contador;
        print("Iteración: ", contador, " Suma actual: ", suma);
        contador = contador + 1;
    };
    
    print("Suma final: ", suma);
}
end
""",
    
    "functions": """
program funciones;
var
    resultado, num1, num2 : int;

void sumar(a : int, b : int)
[
    var res : int;
    {
        res = a + b;
        print("La suma es: ", res);
    }
];

void multiplicar(c : int, d : int)
[
    var res : int;
    {
        res = c * d;
        print("El producto es: ", res);
    }
];

main {
    num1 = 8;
    num2 = 3;
    
    sumar(num1, num2);
    multiplicar(num1, num2);
    
    sumar(5, 7);
    multiplicar(num1 + 2, num2 * 2);
}
end
""",
"float_operations": """
program operaciones_flotantes;
var
    x : float;
    y : int;
    z : float;

main {
    x = 3.5;
    y = 2;
    
    z = x * y + 1.5;
    print("Resultado flotante: ", z);
}
end
""",
"negative_values": """
program negativos;
var
    a, b : int;
    resultado : int;

main {
    a = -5;
    b = 3;
    resultado = a + b;
    print("Resultado con negativos: ", resultado);
}
end
"""
}

def capture_quadruples(code):
    """Run parse_program and capture the quadruples output."""
    # Create a StringIO object to capture stdout
    output = io.StringIO()
    
    # Redirect stdout to our StringIO object
    with redirect_stdout(output):
        ast, errors = parse_program(code)
    
    # Get the captured output
    quadruples_output = output.getvalue()
    
    return ast, errors, quadruples_output

def run_test(test_name, program_code):
    """Run a test with the given program code and log the results."""
    logger.info(f"======== TESTING: {test_name} ========")
    logger.info(f"Program code:\n{program_code}")
    
    try:
        # Parse the program and capture quadruples output
        ast, errors, quadruples = capture_quadruples(program_code)
        
        # Log the results
        if errors:
            logger.warning("Compilation errors:")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("Compilation successful!")
        
        # Log the quadruples
        logger.info("QUADRUPLES:")
        if quadruples.strip():
            logger.info(f"\n{quadruples}")
        else:
            logger.info("No quadruples generated.")
        
        logger.info(f"======== END TEST: {test_name} ========\n")
        return True
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        logger.info(f"======== END TEST: {test_name} ========\n")
        return False

def save_program_to_file(program_name, program_code):
    """Save a test program to a file."""
    folder = "test_programs"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = os.path.join(folder, f"{program_name}.txt")
    with open(filename, 'w') as f:
        f.write(program_code)
    
    return filename

def run_all_tests():
    """Run all predefined tests."""
    logger.info("Starting test suite")
    logger.info(f"Date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save test programs to files
    for name, code in TEST_PROGRAMS.items():
        filename = save_program_to_file(name, code)
        logger.info(f"Saved test program '{name}' to {filename}")
    
    # Run each test
    results = {}
    for name, code in TEST_PROGRAMS.items():
        logger.info(f"\nRunning test: {name}")
        success = run_test(name, code)
        results[name] = "PASS" if success else "FAIL"
    
    # Print summary
    logger.info("\n======== TEST SUMMARY ========")
    for name, result in results.items():
        logger.info(f"{name}: {result}")
    
    logger.info("\nTest suite completed")

def run_single_test(test_name):
    """Run a single test by name."""
    if test_name not in TEST_PROGRAMS:
        logger.error(f"Test '{test_name}' not found")
        return
    
    run_test(test_name, TEST_PROGRAMS[test_name])

def run_custom_file(filename):
    """Run a test with code from a custom file."""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        run_test(os.path.basename(filename), code)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
    except Exception as e:
        logger.error(f"Error reading file {filename}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Test the compiler with various programs')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='Run all predefined tests')
    group.add_argument('--test', choices=TEST_PROGRAMS.keys(), help='Run a specific test')
    group.add_argument('--file', help='Run a test with code from a file')
    
    args = parser.parse_args()
    
    if args.all:
        run_all_tests()
    elif args.test:
        run_single_test(args.test)
    elif args.file:
        run_custom_file(args.file)
    else:
        # Default: run all tests
        run_all_tests()

if __name__ == "__main__":
    main()