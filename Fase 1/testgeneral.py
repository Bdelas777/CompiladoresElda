#!/usr/bin/env python3
"""
Test Generator para el compilador con logging de resultados
Ejecuta múltiples casos de prueba y registra los resultados en un archivo log
"""

import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
import os
from yacc import execute_program, parse_program 

class TestLogger:
    def __init__(self, log_file="test_results.log"):
        self.log_file = log_file
        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log(self, message, print_console=True):
        """Escribe mensaje tanto al archivo log como a la consola"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
        if print_console:
            print(message)
    
    def start_session(self):
        """Inicia una nueva sesión de pruebas"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\n{'='*80}\nSESIÓN DE PRUEBAS - {timestamp}\n{'='*80}\n"
        self.log(header)
    
    def test_case(self, name, code, expected_outputs):
        """Ejecuta un caso de prueba y registra los resultados"""
        self.test_count += 1
        self.log(f"\n[TEST {self.test_count}] {name}")
        self.log("-" * 60)
        
        # Capturar toda la salida del programa
        captured_output = io.StringIO()
        captured_error = io.StringIO()
        
        try:
            with redirect_stdout(captured_output), redirect_stderr(captured_error):
                result = execute_program(code)
            
            output_lines = captured_output.getvalue().strip()
            error_lines = captured_error.getvalue().strip()
            
            self.log("CÓDIGO:")
            for i, line in enumerate(code.strip().split('\n'), 1):
                self.log(f"{i:2}: {line}")
            
            self.log("\nSALIDA OBTENIDA:")
            if output_lines:
                self.log(output_lines)
            else:
                self.log("(Sin salida)")
            
            if error_lines:
                self.log("\nERRORES/DEBUG:")
                self.log(error_lines)
            
            self.log("\nRESULTADOS ESPERADOS:")
            for expected in expected_outputs:
                self.log(f"  - {expected}")
            
            # Verificar si la salida contiene los resultados esperados
            success = self._verify_output(output_lines, expected_outputs)
            
            if success:
                self.log("\n✅ PRUEBA EXITOSA")
                self.passed_tests += 1
            else:
                self.log("\n❌ PRUEBA FALLIDA")
                self.failed_tests += 1
                
        except Exception as e:
            self.log(f"\n❌ ERROR EN EJECUCIÓN: {str(e)}")
            self.failed_tests += 1
        
        self.log("-" * 60)
    
    def _verify_output(self, output, expected_outputs):
        """Verifica si la salida contiene los resultados esperados"""
        if not output:
            return len(expected_outputs) == 0
        
        # Convertir salida a minúsculas para comparación más flexible
        output_lower = output.lower()
        
        for expected in expected_outputs:
            expected_lower = str(expected).lower()
            if expected_lower not in output_lower:
                return False
        return True
    
    def end_session(self):
        """Finaliza la sesión de pruebas y muestra resumen"""
        summary = f"""
{'='*80}
RESUMEN DE PRUEBAS
{'='*80}
Total de pruebas: {self.test_count}
Pruebas exitosas: {self.passed_tests}
Pruebas fallidas: {self.failed_tests}
Porcentaje de éxito: {(self.passed_tests/self.test_count*100) if self.test_count > 0 else 0:.1f}%
{'='*80}
"""
        self.log(summary)

def run_all_tests():
    """Ejecuta todos los casos de prueba definidos"""
    
    # Inicializar logger
    logger = TestLogger("test_results.log")
    
    # Limpiar archivo log anterior
    if os.path.exists("test_results.log"):
        os.remove("test_results.log")
    
    logger.start_session()
    
    # Test 1: Operaciones Básicas
    test1_code = '''program operaciones_basicas;
var
    a, b, c, resultado, resultado2 : int;
    resultado3 : float;

main {
    a = 5;
    b = 3;
    c = 2;
    
    resultado = a + b * c;
    print("Resultado 1: ", resultado);
    
    resultado2 = (a + b) * c;
    print("Resultado 2: ", resultado2);
    
    resultado3 = a - b / c;
    print("Resultado 3: ", resultado3);
    
    resultado = a + b + c;
    print("Resultado 4: ", resultado);
    
    resultado2 = a + b * c * 2;
    print("Resultado 5: ", resultado2);
    
    resultado3 = a + b + c * 2;
    print("Resultado 6: ", resultado3);
    
    resultado3 = a  - b * c *2 + 1 ;
    print("Resultado 7: ", resultado3);
}
end'''
    
    test1_expected = ["11", "16", "3.5", "10", "17", "12", "-6"]
    logger.test_case("Operaciones Básicas", test1_code, test1_expected)
    
    # Test 2: Control IF
    test2_code = '''program control_if;
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
end'''
    
    test2_expected = ["El mayor es x:", "15", "x es mayor o igual que 10"]
    logger.test_case("Control IF", test2_code, test2_expected)
    
    # Test 3: Ciclo WHILE
    test3_code = '''program ciclo_while;
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
end'''
    
    test3_expected = ["Iteración:", "1", "Suma actual:", "1", "Iteración:", "2", "Suma actual:", "3", 
                     "Iteración:", "3", "Suma actual:", "6", "Iteración:", "4", "Suma actual:", "10", "Suma final:", "10"]
    logger.test_case("Ciclo WHILE", test3_code, test3_expected)
    
    # Test 4: Funciones
    test4_code = '''program funciones;
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
end'''
    
    test4_expected = ["La suma es:", "11", "El producto es:", "24", "La suma es:", "12", "El producto es:", "60"]
    logger.test_case("Funciones", test4_code, test4_expected)
    
    # Test 5: Operaciones Flotantes
    test5_code = '''program operaciones_flotantes;
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
end'''
    
    test5_expected = ["8.5"]
    logger.test_case("Operaciones Flotantes", test5_code, test5_expected)
    
    # Test 6: Números Negativos
    test6_code = '''program negativos;
var
    a, b : int;
    resultado : int;

main {
    a = -5;
    b = 3;
    resultado = a + b;
    print("Resultado con negativos: ", resultado);
}
end'''
    
    test6_expected = ["-2"]
    logger.test_case("Números Negativos", test6_code, test6_expected)
    
    # Test 7: Factorial con Función
    test7_code = '''program factorial_funcion;
var
    numero, resultado : int;

void calcular_factorial(n : int)
[
    var factorial, i : int;
    {
        factorial = 1;
        i = 1;
        
        print("Calculando factorial de ", n);
        
        while (i < n + 1) do {
            factorial = factorial * i;
            print("Paso ", i, ": ", factorial);
            i = i + 1;
        };
        
        print("Factorial de ", n, " es: ", factorial);
    }
];

main {
    numero = 5;
    calcular_factorial(numero);
    
    calcular_factorial(4);
    calcular_factorial(6);
}
end'''
    
    test7_expected = ["Calculando factorial de", "5", "Paso", "1", ":", "1", 
                     "Paso", "2", ":", "2", "Paso", "3", ":", "6",
                     "Paso", "4", ":", "24", "Paso", "5", ":", "120",
                     "Factorial de", "5", "es:", "120", "Calculando factorial de", "4",
                     "Factorial de", "4", "es:", "24", "Calculando factorial de", "6",
                     "Factorial de", "6", "es:", "720"]
    logger.test_case("Factorial con Función", test7_code, test7_expected)
    
    # Test 8: Fibonacci con Función
    test8_code = '''program fibonacci_funcion;
var
    cantidad : int;

void generar_fibonacci(n : int)
[
    var i, fib1, fib2, siguiente : int;
    {
        fib1 = 0;
        fib2 = 1;
        
        print("Serie de Fibonacci de ", n, " términos:");
        
        if (n > 2) {
            print("F(1) = ", fib1);
        };
        
        if (n > 3) {
            print("F(2) = ", fib2);
        };
        
        i = 3;
        while (i < n + 1) do {
            siguiente = fib1 + fib2;
            print("F(", i, ") = ", siguiente);
            fib1 = fib2;
            fib2 = siguiente;
            i = i + 1;
        };
        
        print("Serie completada");
    }
];

void mostrar_fibonacci_hasta(limite : int)
[
    var fib1, fib2, siguiente : int;
    {
        fib1 = 0;
        fib2 = 1;
        
        print("Fibonacci hasta ", limite, ":");
        print(fib1);
        
        if (fib2 < limite + 1) {
            print(fib2);
        };
        
        siguiente = fib1 + fib2;
        while (siguiente < limite + 1) do {
            print(siguiente);
            fib1 = fib2;
            fib2 = siguiente;
            siguiente = fib1 + fib2;
        };
    }
];

main {
    cantidad = 7;
    generar_fibonacci(cantidad);
    
    mostrar_fibonacci_hasta(20);
}
end'''
    
    test8_expected = ["Serie de Fibonacci de", "7", "términos:", "F(1) =", "0", 
                     "F(2) =", "1", "F(", "3", ") =", "1", "F(", "4", ") =", "2",
                     "F(", "5", ") =", "3", "F(", "6", ") =", "5", "F(", "7", ") =", "8",
                     "Serie completada", "Fibonacci hasta", "20", "0", "1", "1", "2", "3", "5", "8", "13"]
    logger.test_case("Fibonacci con Función", test8_code, test8_expected)
    
    
    # Test 9: Funciones Matemáticas Avanzadas
    test9_code = '''program funciones_matematicas;
var
    num1, num2, resultado : int;

void potencia(base : int, exponente : int)
[
    var resultado, i : int;
    {
        resultado = 1;
        i = 1;
        
        while (i < exponente + 1) do {
            resultado = resultado * base;
            i = i + 1;
        };
        
        print(base, " elevado a ", exponente, " = ", resultado);
    }
];

void tabla_multiplicar(numero : int)
[
    var i, producto : int;
    {
        print("Tabla del ", numero, ":");
        i = 1;
        while (i < 11) do {
            producto = numero * i;
            print(numero, " x ", i, " = ", producto);
            i = i + 1;
        };
    }
];

void mcd(a : float, b : float)
[
    var temp : float;
    {
        print("Calculando MCD de ", a, " y ", b);
        
        while (b != 0) do {
            temp = b;
            b = a - (a / b) * b;
            a = temp;
        };
        
        print("MCD = ", a);
    }
];

main {
    potencia(2, 5);
    potencia(3, 4);
    
    tabla_multiplicar(7);
    
    mcd(48, 18);
}
end'''
    
    test9_expected = ["2", "elevado a", "5", "=", "32", "3", "elevado a", "4", "=", "81",
                     "Tabla del", "7", "7", "x", "1", "=", "7", "7", "x", "10", "=", "70",
                     "Calculando MCD de", "48", "y", "18", "MCD =", "6"]
    logger.test_case("Funciones Matemáticas Avanzadas", test9_code, test9_expected)
    
    
    # Test 10: Funciones con Parámetros Múltiples 
    test10_code = '''program funciones_parametros;
var
    a, b, c : int;
    resultado : float;

void operaciones_basicas(x : int, y : int, z : int)
[
    var suma, producto, promedio : int;
    {
        suma = x + y + z;
        producto = x * y * z;
        promedio = suma / 3;
        
        print("Números: ", x, ", ", y, ", ", z);
        print("Suma: ", suma);
        print("Producto: ", producto);
        print("Promedio: ", promedio);
    }
];

void comparar_numeros(num1 : int, num2 : int)
[
    {
        print("Comparando ", num1, " y ", num2);
        
        if (num1 > num2) {
            print(num1, " es mayor que ", num2);
        } else {
            if (num1 < num2) {
                print(num1, " es menor que ", num2);
            } else {
                print(num1, " es igual a ", num2);
            };
        };
    }
];

void serie_aritmetica(inicio : int, diferencia : int, terminos : int)
[
    var i, valor : int;
    {
        print("Serie aritmética:");
        print("Inicio: ", inicio, ", Diferencia: ", diferencia, ", Términos: ", terminos);
        
        i = 0;
        valor = inicio;
        while (i < terminos) do {
            print("Término ", i + 1, ": ", valor);
            valor = valor + diferencia;
            i = i + 1;
        };
    }
];

main {
    operaciones_basicas(4, 7, 2);
    
    comparar_numeros(15, 8);
    comparar_numeros(5, 12);
    comparar_numeros(9, 9);
    
    serie_aritmetica(5, 3, 6);
}
end'''
    
    test10_expected = ["Números:", "4", ",", "7", ",", "2", "Suma:", "13", "Producto:", "56", "Promedio:", "4",
                      "Comparando", "15", "y", "8", "15", "es mayor que", "8",
                      "Comparando", "5", "y", "12", "5", "es menor que", "12", 
                      "Comparando", "9", "y", "9", "9", "es igual a", "9",
                      "Serie aritmética:", "Inicio:", "5", "Diferencia:", "3", "Términos:", "6",
                      "Término", "1", ":", "5", "Término", "6", ":", "20"]
    logger.test_case("Funciones con Parámetros Múltiples", test10_code, test10_expected)
    
    # Finalizar sesión de pruebas
    logger.end_session()
    
    print(f"\n🔍 Los resultados detallados se han guardado en: {logger.log_file}")
    print(f"📊 Resumen: {logger.passed_tests}/{logger.test_count} pruebas exitosas")

if __name__ == "__main__":
    print("🚀 Iniciando suite de pruebas del compilador...")
    print("=" * 60)
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Suite de pruebas completada")