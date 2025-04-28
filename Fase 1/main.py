# test_babyduck.py - Sistema de pruebas para el compilador BabyDuck
import sys
import datetime
import traceback
from io import StringIO
import ply.yacc as yacc
import ply.lex as lex

# Importar el lexer y parser (asumiendo que están en los archivos lex.py y yacc.py)
from lex import lexer, tokens
from yacc import parser

# Categorías de pruebas
lexer_tests = [
    ("L-ID-01", "variable", "Identificador simple"),
    ("L-ID-02", "var1_name2", "Identificador con números y guiones"),
    ("L-ID-03", "1invalid", "Identificador inválido (empieza con número)"),
    ("L-ID-04", "_invalid", "Identificador inválido (empieza con guión)"),
    ("L-INT-01", "123", "Entero válido"),
    ("L-INT-02", "-123", "Entero con signo negativo (se tokenizará como TOKEN_MINUS y TOKEN_CTE_INT)"),
    ("L-FLOAT-01", "123.45", "Flotante válido"),
    ("L-FLOAT-02", "123.", "Flotante inválido (falta parte decimal)"),
    ("L-FLOAT-03", ".45", "Flotante inválido (falta parte entera)"),
    ("L-STR-01", '"Hello world"', "String válido"),
    ("L-STR-02", '"Cadena con "comillas""', "String inválido (comillas dentro)"),
    ("L-RES-01", "program var int float if else while do print void main end", "Palabras reservadas"),
    ("L-OP-01", "+ - * / > < != =", "Operadores"),
    ("L-SYM-01", "; , : ( ) { }", "Símbolos especiales")
]

# Pruebas para la estructura del programa
parser_program_tests = [
    ("P-STRUCT-01", """
    program MyProgram;
    main {
    }
    end
    """, "Programa mínimo válido"),
    
    ("P-STRUCT-02", """
    program MyProgram;
    var x: int;
    main {
    }
    end
    """, "Programa con declaración de variable"),
    
    ("P-STRUCT-03", """
    program;
    main {
    }
    end
    """, "Programa sin identificador (inválido)"),
    
    ("P-STRUCT-04", """
    program MyProgram
    main {
    }
    end
    """, "Programa sin punto y coma después del identificador (inválido)"),
    
    ("P-STRUCT-05", """
    program MyProgram;
    main {
    }
    """, "Programa sin 'end' (inválido)"),
    
    ("P-STRUCT-06", """
    MyProgram;
    main {
    }
    end
    """, "Programa sin palabra clave 'program' (inválido)")
]

# Pruebas para declaraciones de variables
parser_var_tests = [
    ("P-VAR-01", """
    program Test;
    var x: int;
    main {
    }
    end
    """, "Declaración de variable simple"),
    
    ("P-VAR-02", """
    program Test;
    var x, y, z: int;
    main {
    }
    end
    """, "Declaración de múltiples variables del mismo tipo"),
    
    ("P-VAR-03", """
    program Test;
    var x: int;
    var y: float;
    main {
    }
    end
    """, "Declaración de variables de diferentes tipos"),
    
    ("P-VAR-04", """
    program Test;
    var x: int
    main {
    }
    end
    """, "Declaración de variable sin punto y coma (inválido)"),
    
    ("P-VAR-05", """
    program Test;
    var x int;
    main {
    }
    end
    """, "Declaración de variable sin dos puntos (inválido)"),
    
    ("P-VAR-06", """
    program Test;
    var x, y,: int;
    main {
    }
    end
    """, "Declaración de variable con coma adicional (inválido)"),
    
    ("P-VAR-07", """
    program Test;
    var x: string;
    main {
    }
    end
    """, "Declaración de variable con tipo no soportado (inválido)")
]

# Pruebas para declaraciones de funciones
parser_func_tests = [
    ("P-FUNC-01", """
    program Test;
    void func() {
    };
    main {
    }
    end
    """, "Función simple"),
    
    ("P-FUNC-02", """
    program Test;
    void func(x: int) {
    };
    main {
    }
    end
    """, "Función con un parámetro"),
    
    ("P-FUNC-03", """
    program Test;
    void func(x: int, y: float) {
    };
    main {
    }
    end
    """, "Función con múltiples parámetros"),
    
    ("P-FUNC-04", """
    program Test;
    void func() 
    var local: int;
    {
        local = 10;
    };
    main {
    }
    end
    """, "Función con variable local"),
    
    ("P-FUNC-05", """
    program Test;
    void func() {
        x = 5;
    };
    main {
    }
    end
    """, "Función con sentencia de asignación"),
    
    ("P-FUNC-06", """
    program Test;
    void func() {
    }
    main {
    }
    end
    """, "Función sin punto y coma final (inválido)"),
    
    ("P-FUNC-07", """
    program Test;
    void func {
    };
    main {
    }
    end
    """, "Función sin paréntesis (inválido)")
]

# Pruebas para sentencias
parser_statement_tests = [
    # Asignaciones
    ("P-ASSIGN-01", """
    program Test;
    main {
        x = 5;
    }
    end
    """, "Asignación simple"),
    
    ("P-ASSIGN-02", """
    program Test;
    main {
        x = y + 10;
    }
    end
    """, "Asignación con expresión"),
    
    ("P-ASSIGN-03", """
    program Test;
    main {
        x = (y + 2) * 3;
    }
    end
    """, "Asignación con expresión compleja"),
    
    ("P-ASSIGN-04", """
    program Test;
    main {
        x = 5
    }
    end
    """, "Asignación sin punto y coma (inválido)"),
    
    ("P-ASSIGN-05", """
    program Test;
    main {
        5 = x;
    }
    end
    """, "Asignación inválida (constante en lado izquierdo)"),
    
    # Condicionales
    ("P-IF-01", """
    program Test;
    main {
        if (x > 5) {
            y = 1;
        };
    }
    end
    """, "Condicional simple"),
    
    ("P-IF-02", """
    program Test;
    main {
        if (x > 5) {
            y = 1;
        } else {
            y = 0;
        };
    }
    end
    """, "Condicional con else"),
    
    ("P-IF-03", """
    program Test;
    main {
        if (x > 5) {
            if (y < 10) {
                z = 1;
            };
        };
    }
    end
    """, "Condicionales anidados"),
    
    ("P-IF-04", """
    program Test;
    main {
        if x > 5 {
            y = 1;
        };
    }
    end
    """, "Condicional sin paréntesis (inválido)"),
    
    ("P-IF-05", """
    program Test;
    main {
        if (x > 5) {
            y = 1;
        }
    }
    end
    """, "Condicional sin punto y coma (inválido)"),
    
    # Ciclos
    ("P-WHILE-01", """
    program Test;
    main {
        while (x > 0) do {
            x = x - 1;
        };
    }
    end
    """, "Ciclo while simple"),
    
    ("P-WHILE-02", """
    program Test;
    main {
        while (x > 0) do {
            while (y < 10) do {
                y = y + 1;
            };
        };
    }
    end
    """, "Ciclos while anidados"),
    
    ("P-WHILE-03", """
    program Test;
    main {
        while (x > 0) do {
            y = y + 1;
            x = x - 1;
        };
    }
    end
    """, "Ciclo while con múltiples sentencias"),
    
    ("P-WHILE-04", """
    program Test;
    main {
        while (x > 0) {
            x = x - 1;
        };
    }
    end
    """, "Ciclo while sin palabra 'do' (inválido)"),
    
    ("P-WHILE-05", """
    program Test;
    main {
        while (x > 0) do {
            x = x - 1;
        }
    }
    end
    """, "Ciclo while sin punto y coma (inválido)"),
    
    # Print
    ("P-PRINT-01", """
    program Test;
    main {
        print("Hello");
    }
    end
    """, "Sentencia print con string"),
    
    ("P-PRINT-02", """
    program Test;
    main {
        print(x + y);
    }
    end
    """, "Sentencia print con expresión"),
    
    ("P-PRINT-03", """
    program Test;
    main {
        print("Value:", x, y + z);
    }
    end
    """, "Sentencia print con múltiples valores"),
    
    ("P-PRINT-04", """
    program Test;
    main {
        print "Hello";
    }
    end
    """, "Sentencia print sin paréntesis (inválido)"),
    
    ("P-PRINT-05", """
    program Test;
    main {
        print("Hello")
    }
    end
    """, "Sentencia print sin punto y coma (inválido)"),
    
    # Llamadas a funciones
    ("P-CALL-01", """
    program Test;
    void func() {
    };
    main {
        func();
    }
    end
    """, "Llamada a función simple"),
    
    ("P-CALL-02", """
    program Test;
    void func(x: int) {
    };
    main {
        func(10);
    }
    end
    """, "Llamada a función con argumento"),
    
    ("P-CALL-03", """
    program Test;
    void func(x: int, y: int) {
    };
    main {
        func(x, y + 1);
    }
    end
    """, "Llamada a función con múltiples argumentos"),
    
    ("P-CALL-04", """
    program Test;
    void func() {
    };
    main {
        func;
    }
    end
    """, "Llamada a función sin paréntesis (inválido)"),
    
    ("P-CALL-05", """
    program Test;
    void func() {
    };
    main {
        func()
    }
    end
    """, "Llamada a función sin punto y coma (inválido)")
]

# Pruebas para expresiones
parser_expr_tests = [
    ("P-EXPR-01", """
    program Test;
    main {
        x = a + b;
    }
    end
    """, "Expresión con suma"),
    
    ("P-EXPR-02", """
    program Test;
    main {
        x = a * b;
    }
    end
    """, "Expresión con multiplicación"),
    
    ("P-EXPR-03", """
    program Test;
    main {
        if (a > b) {
            x = 1;
        };
    }
    end
    """, "Expresión con comparación"),
    
    ("P-EXPR-04", """
    program Test;
    main {
        x = (a + b) * (c - 1);
    }
    end
    """, "Expresión compleja con paréntesis"),
    
    ("P-EXPR-05", """
    program Test;
    main {
        x = a + b * c;
    }
    end
    """, "Expresión con precedencia de operadores"),
    
    ("P-EXPR-06", """
    program Test;
    main {
        x = -a;
    }
    end
    """, "Expresión con operador unario"),
    
    ("P-EXPR-07", """
    program Test;
    main {
        x = ((a + b) * c);
    }
    end
    """, "Expresión con paréntesis anidados")
]

# Programas completos
full_programs = [
    ("P-FULL-01", """
    program simple;
    var x: int;
    main {
        x = 5;
        print(x);
    }
    end
    """, "Programa simple con una variable, asignación y print"),
    
    ("P-FULL-02", """
    program withFunctions;
    var x, y: int;

    void increment(val: int) {
        x = val + 1;
    };

    main {
        y = 10;
        increment(y);
        print(x);
    }
    end
    """, "Programa con función y llamada a función"),
    
    ("P-FULL-03", """
    program complex;
    var i, max: int;
    var result: float;

    void calculateSum(limit: int) 
    var sum: int;
    {
        i = 1;
        sum = 0;
        while (i <= limit) do {
            sum = sum + i;
            i = i + 1;
        };
        result = sum;
    };

    main {
        max = 100;
        calculateSum(max);
        
        if (result > 5000) {
            print("Large sum:", result);
        } else {
            print("Small sum:", result);
        };
    }
    end
    """, "Programa complejo con variables, funciones, ciclos y condicionales")
]

# Función para ejecutar pruebas léxicas
def run_lexer_test(test_id, code, description):
    print(f"\n[Test {test_id}] {description}")
    print(f"Code: {code}")
    try:
        # Redireccionar la salida estándar para capturar errores
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        # Ejecutar el lexer
        lexer.input(code)
        tokens_found = []
        for token in lexer:
            tokens_found.append(f"{token.type}('{token.value}')")
        
        # Restaurar la salida estándar
        sys.stdout = old_stdout
        error_output = redirected_output.getvalue()
        
        # Verificar si hubo errores
        if "Illegal character" in error_output:
            print(f"❌ FAILED: {error_output.strip()}")
            return False
        else:
            print(f"✅ PASSED: Tokens encontrados: {', '.join(tokens_found)}")
            return True
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return False

# Función para ejecutar pruebas de parser
def run_parser_test(test_id, code, description):
    print(f"\n[Test {test_id}] {description}")
    print(f"Code:\n{code}")
    
    try:
        # Redireccionar la salida estándar para capturar errores y mensajes de depuración
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        # Parsear el código
        result = parser.parse(code)
        
        # Restaurar la salida estándar
        sys.stdout = old_stdout
        debug_output = redirected_output.getvalue()
        
        # Verificar si hubo errores
        if "ERROR:" in debug_output:
            error_lines = [line for line in debug_output.split('\n') if "ERROR:" in line]
            print(f"❌ FAILED: {'; '.join(error_lines)}")
            return False
        else:
            print(f"✅ PASSED: Análisis sintáctico exitoso")
            # Opcional: mostrar el árbol de sintaxis si es necesario
            # if result:
            #    print(f"AST: {result}")
            return True
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return False

def run_all_tests(test_categories=None):
    results = {
        "lexer": {"passed": 0, "failed": 0},
        "parser_program": {"passed": 0, "failed": 0},
        "parser_var": {"passed": 0, "failed": 0},
        "parser_func": {"passed": 0, "failed": 0},
        "parser_statement": {"passed": 0, "failed": 0},
        "parser_expr": {"passed": 0, "failed": 0},
        "full_programs": {"passed": 0, "failed": 0}
    }
    
    print("==== 🚀 Test Run Started ====")
    print(f"🕒 {datetime.datetime.now()}\n")
    
    # Si no se especifican categorías, ejecutar todas
    if not test_categories:
        test_categories = list(results.keys())
    
    if "lexer" in test_categories:
        print("==== 🧪 Lexer Tests ====")
        for test_id, code, description in lexer_tests:
            if run_lexer_test(test_id, code, description):
                results["lexer"]["passed"] += 1
            else:
                results["lexer"]["failed"] += 1
    
    if "parser_program" in test_categories:
        print("\n==== 📐 Parser Program Structure Tests ====")
        for test_id, code, description in parser_program_tests:
            if run_parser_test(test_id, code, description):
                results["parser_program"]["passed"] += 1
            else:
                results["parser_program"]["failed"] += 1
    
    if "parser_var" in test_categories:
        print("\n==== 📦 Parser Variable Tests ====")
        for test_id, code, description in parser_var_tests:
            if run_parser_test(test_id, code, description):
                results["parser_var"]["passed"] += 1
            else:
                results["parser_var"]["failed"] += 1
    
    if "parser_func" in test_categories:
        print("\n==== 🔧 Parser Function Tests ====")
        for test_id, code, description in parser_func_tests:
            if run_parser_test(test_id, code, description):
                results["parser_func"]["passed"] += 1
            else:
                results["parser_func"]["failed"] += 1
    
    if "parser_statement" in test_categories:
        print("\n==== 📝 Parser Statement Tests ====")
        for test_id, code, description in parser_statement_tests:
            if run_parser_test(test_id, code, description):
                results["parser_statement"]["passed"] += 1
            else:
                results["parser_statement"]["failed"] += 1
    
    if "parser_expr" in test_categories:
        print("\n==== 🧮 Parser Expression Tests ====")
        for test_id, code, description in parser_expr_tests:
            if run_parser_test(test_id, code, description):
                results["parser_expr"]["passed"] += 1
            else:
                results["parser_expr"]["failed"] += 1
    
    if "full_programs" in test_categories:
        print("\n==== 🧑‍💻 Full Program Tests ====")
        for test_id, code, description in full_programs:
            if run_parser_test(test_id, code, description):
                results["full_programs"]["passed"] += 1
            else:
                results["full_programs"]["failed"] += 1
    
    # Resumen de resultados
    print("\n==== 📊 Test Summary ====")
    total_passed = 0
    total_failed = 0
    
    for category, stats in results.items():
        if category in test_categories:
            passed = stats["passed"]
            failed = stats["failed"]
            total = passed + failed
            if total > 0:
                percent = (passed / total) * 100
                print(f"{category}: {passed}/{total} passed ({percent:.1f}%)")
                total_passed += passed
                total_failed += failed
    
    grand_total = total_passed + total_failed
    if grand_total > 0:
        overall_percent = (total_passed / grand_total) * 100
        print(f"\nOVERALL: {total_passed}/{grand_total} passed ({overall_percent:.1f}%)")
    
    print("\n==== ✅ Test Run Complete ====")
    print(f"🕒 {datetime.datetime.now()}")

def run_tests():
    test_cases = (
        lexer_tests +
        parser_program_tests +
        parser_var_tests +
        parser_func_tests +
        parser_statement_tests + 
        parser_expr_tests  + 
        full_programs
    )
    
    log_output = StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = log_output
    sys.stderr = log_output

    print(f"== INICIO DE PRUEBAS - {datetime.datetime.now()} ==\n")

    for code, input_text, description in test_cases:
        print(f"[{code}] {description}")
        print("Código:")
        print(input_text.strip())
        try:
            if code.startswith("L-"):
                lexer.input(input_text)
                tokens_list = []
                while True:
                    tok = lexer.token()
                    if not tok:
                        break
                    tokens_list.append((tok.type, tok.value))
                print("Tokens:", tokens_list)
            elif code.startswith("P-"):
                result = parser.parse(input_text, lexer=lexer)
                print("Resultado del parser:", result)
        except Exception as e:
            print("Error durante la prueba:")
            traceback.print_exc()
        print("-" * 80)

    print(f"\n== FIN DE PRUEBAS - {datetime.datetime.now()} ==\n")

    sys.stdout = original_stdout
    sys.stderr = original_stderr

    with open("test_log5.log", "w", encoding="utf-8") as f:
        f.write(log_output.getvalue())
    print("Pruebas completadas. Resultados guardados en test_results.log")


if __name__ == "__main__":
    run_tests()
