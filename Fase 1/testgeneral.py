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