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

# Casos de prueba

test_code1 = """
program test1;

var
    i, j, k, a : int;
    x, y : float;

void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];

main {
    a = 1 + 2;
}

end
"""

test_code2 = """
program test2;

var
    i, j,a, k, k : int;
    x, y : float;

void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];

main {
    a = 1 + 2;
}

end
"""

test_code3 = """
program pelos;

var
    i, j, k,a  : int;
    x, y : float;

void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];

void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];

main {
    a = 1 + 2;
}

end
"""

test_code4 = """
program uno;

var
    i, j, k ,a : int;
    x, y : float;

void uno(i : int)
[
    var x : int;
    {
        x = 1;
    }
];

main {
    a = 1 + 2;
}

end
"""

test_code5 = """
program sinmain;

var a : int;

void saluda() [
    {
        a = 3;
    }
];

end
"""

test_code6 = """
program errorparam;

var a : int;

void prueba(x : entero) [  
    {
        a = 3;
    }
];

main {
    a = 1;
}

end
"""

test_code7 = """
program undeclared_var;

main {
    a = 5;  
}

end
"""

test_code8 = """
program wrongtype;

var a : int;

main {
    a = 3.5; 
}

end
"""

test_code9 = """
program nameconflict;

var prueba : int;

void prueba() [  
    {
        prueba = 3;
    }
];

main {
    prueba = 1;
}

end
"""

test_code10 = """
program callfunc;

main {
    uno(); 
}

end
"""

# Función para correr cada prueba
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


# Ejecutar todas las pruebas
def run_tests():
    test_cases = [
        ("P-FUNC-01", test_code1, "Funcion con parametros correctos"),
        ("P-FUNC-02", test_code2, "Funcion con variable doblemente declarada"),
        ("P-FUNC-03", test_code3, "Funciones duplicadas"),
        ("P-FUNC-04", test_code4, "Funcion y main sin errores"),
        ("P-FUNC-05", test_code5, "Programa sin main"),
        ("P-FUNC-07", test_code7, "Uso de variable no declarada"),
        ("P-FUNC-08", test_code8, "Asignación con error de tipo"),
        ("P-FUNC-09", test_code9, "Polimorfismo en un nombre"),
        ("P-FUNC-10", test_code10, "Llamada a función no declarada")
    ]

    logging.info(f"== INICIO DE PRUEBAS - {datetime.datetime.now()} ==\n")

    for code, input_text, description in test_cases:
        run_test(input_text, f"{code} - {description}")

    logging.info(f"\n== FIN DE PRUEBAS - {datetime.datetime.now()} ==\n")
    print("Pruebas completadas. Resultados guardados en prueba.log")


if __name__ == "__main__":
    print("\nTesting BabyDuck parameter handling\n")
    run_tests()
