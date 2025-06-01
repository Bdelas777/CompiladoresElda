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
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
        if print_console:
            print(message)
    
    def start_session(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\n{'='*80}\nSESIÓN DE PRUEBAS - {timestamp}\n{'='*80}\n"
        self.log(header)
    
    def test_case(self, name, code, expected_outputs):
        self.test_count += 1
        self.log(f"\n[TEST {self.test_count}] {name}")
        self.log("-" * 60)
        
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
        if not output:
            return len(expected_outputs) == 0
        
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
    
    logger = TestLogger("test_results.log")
    
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
    
    test1_expected = ["11", "16", "4", "10", "17", "12", "-6"]
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
    
    # Test 11: FOR con Función 
    test11_code = '''program for_con_funcion;
var
    limite : int;

void contar_hasta(n : int)
[
    var i, contador : int;
    {
        print("Contando hasta ", n, ":");
        contador = 0;
        
        for (i = 1; i < n + 1; i = i + 1) do {
            contador = contador + 1;
            print("Contador: ", contador, " (i = ", i, ")");
        };
        
        print("Terminé de contar hasta ", n);
    }
];

void tabla_cuadrados(hasta : int)
[
    var i, cuadrado : int;
    {
        print("Tabla de cuadrados hasta ", hasta, ":");
        
        for (i = 1; i < hasta + 1; i = i + 1) do {
            cuadrado = i * i;
            print(i, " al cuadrado = ", cuadrado);
        };
    }
];

main {
    limite = 5;
    
    contar_hasta(limite);
    
    tabla_cuadrados(4);
    
    print("FOR anidado:");
    for (limite = 1; limite < 4; limite = limite + 1) do {
        print("Tabla del ", limite, ":");
        contar_hasta(limite);
    };
}
end'''
    
    test11_expected = ["Contando hasta", "5", "Contador:", "1", "(i =", "1", ")", 
                     "Contador:", "5", "(i =", "5", ")", "Terminé de contar hasta", "5",
                     "Tabla de cuadrados hasta", "4", "1", "al cuadrado =", "1",
                     "4", "al cuadrado =", "16", "FOR anidado:", "Tabla del", "1",
                     "Tabla del", "3", "Terminé de contar hasta", "3"]
    logger.test_case("FOR con Función", test11_code, test11_expected)
    
    # Test 12: Calculadora Avanzada 
    test12_code = '''program calculadora_avanzada;
var 
    num1, num2, num3, resultado, factorial_num : int;
    promedio_val : int;
    
int calcular_factorial(n : int)
[
    var i, fact : int;
    {
        fact = 1;
        i = 1;
        while (i < n + 1) do {
            fact = fact * i;
            i = i + 1;
        };
        return fact;
    }
];

int potencia(base : int, exponente : int)
[
    var i, resultado : int;
    {
        resultado = 1;
        i = 1;
        while (i < exponente + 1) do {
            resultado = resultado * base;
            i = i + 1;
        };
        return resultado;
    }
];

int maximo_de_tres(a : int, b : int, c : int)
[
    var max : int;
    {
        max = a;
        if (b > max) {
            max = b;
        };
        if (c > max) {
            max = c;
        };
        return max;
    }
];

void mostrar_tabla_multiplicar(numero : int, limite : int)
[
    var i, producto : int;
    {
        print("Tabla de multiplicar del ", numero, ":");
        i = 1;
        while (i < limite + 1) do {
            producto = numero * i;
            print(numero, " x ", i, " = ", producto);
            i = i + 1;
        };
    }
];

void analizar_numero(num : int)
[
    {
        print("Analizando el número: ", num);
        
        if (num > 0) {
            print("El número es positivo");
        } else {
            if (num < 0) {
                print("El número es negativo");
            } else {
                print("El número es cero");
            };
        };
                
        if (num > 0) {
            print("El número es par");
        } else {
            print("El número es impar");
        };
    }
];

void mostrar_operaciones_basicas(a : int, b : int)
[
    var suma, resta, multiplicacion, division : int;
    {
        suma = a + b;
        resta = a - b;
        multiplicacion = a * b;
        
        print("Operaciones básicas entre ", a, " y ", b, ":");
        print("Suma: ", suma);
        print("Resta: ", resta);
        print("Multiplicación: ", multiplicacion);
        
        if (b > 0) {
            division = a / b;
            print("División: ", division);
        } else {
            print("No se puede dividir entre cero");
        };
    }
];

int calcular_promedio(a : int, b : int, c : int)
[
    var suma, promedio : int;
    {
        suma = a + b + c;
        promedio = suma / 3;
        return promedio;
    }
];


main {
    print("=== CALCULADORA AVANZADA ===");
    
    num1 = 12;
    num2 = 8;
    num3 = 15;
    
    print("Números de trabajo: ", num1, ", ", num2, ", ", num3);
    print("");
    
    mostrar_operaciones_basicas(num1, num2);
    print("");
    
    analizar_numero(num1);
    print("");
    
    mostrar_tabla_multiplicar(num2, 5);
    print("");
    
    factorial_num = 5;
    resultado = calcular_factorial(factorial_num);
    print("Factorial de ", factorial_num, " es: ", resultado);
    
    resultado = potencia(num2, 3);
    print(num2, " elevado a la 3 es: ", resultado);
    
    resultado = maximo_de_tres(num1, num2, num3);
    print("El mayor de los tres números es: ", resultado);
    
    promedio_val = calcular_promedio(num1, num2, num3);
    print("El promedio de los tres números es: ", promedio_val);
    print("");
    
    
    print("=== FIN DEL PROGRAMA ===");
}
end'''
    
    test12_expected = ["=== CALCULADORA AVANZADA ===", "Números de trabajo:", "12", ",", "8", ",", "15",
                      "Operaciones básicas entre", "12", "y", "8", "Suma:", "20", "Resta:", "4", 
                      "Multiplicación:", "96", "División:", "1", "Analizando el número:", "12",
                      "El número es positivo", "El número es par", "Tabla de multiplicar del", "8",
                      "8", " x ", "1", " = ", "8", "8", " x ", "5", " = ", "40",
                      "Factorial de", "5", "es:", "120", "8", "elevado a la 3 es:", "512",
                      "El mayor de los tres números es:", "15", "El promedio de los tres números es:", "11",
                      "=== FIN DEL PROGRAMA ==="]
    logger.test_case("Calculadora Avanzada", test12_code, test12_expected)
    
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