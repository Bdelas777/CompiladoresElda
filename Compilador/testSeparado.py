import sys
import io
import os
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from yacc import execute_program, parse_program 

class SimpleTestRunner:
    def __init__(self):
        self.tests_folder = "testsPorSeparado"
        self.test_definitions = {
            "1_operaciones_basicas.txt": ["11", "16", "4.0", "10", "17", "12", "-6"],
            "2_control_if.txt": ["El mayor es x:", "15", "x es mayor o igual que 10"],
            "3_ciclo_while.txt": ["Iteración:", "1", "Suma actual:", "1", "Iteración:", "2", "Suma actual:", "3", 
                               "Iteración:", "3", "Suma actual:", "6", "Iteración:", "4", "Suma actual:", "10", "Suma final:", "10"],
            "4_funciones.txt": ["La suma es:", "11", "El producto es:", "24", "La suma es:", "12", "El producto es:", "60"],
            "5_operaciones_flotantes.txt": ["8.5"],
            "6_negativos.txt": ["-2"],
            "7_factorial_funcion.txt": ["Calculando factorial de", "5", "Paso", "1", ":", "1", 
                                      "Paso", "2", ":", "2", "Paso", "3", ":", "6",
                                      "Paso", "4", ":", "24", "Paso", "5", ":", "120",
                                      "Factorial de", "5", "es:", "120"],
            "8_fibonacci_funcion.txt": ["Serie de Fibonacci de", "7", "términos:", "F(1) =", "0", 
                                      "F(2) =", "1", "F(", "3", ") =", "1", "F(", "4", ") =", "2"],
            "9_funciones_matematicas.txt": ["2", "elevado a", "5", "=", "32", "3", "elevado a", "4", "=", "81"],
            "10_funciones_parametros.txt": ["Números:", "4", ",", "7", ",", "2", "Suma:", "13", "Producto:", "56"],
            "11_for_con_funcion.txt": ["Contando hasta", "5", "Contador:", "1", "(i =", "1", ")", 
                                     "Contador:", "5", "(i =", "5", ")", "Terminé de contar hasta", "5"],
            "12_calculadora_avanzada.txt": ["=== CALCULADORA AVANZADA ===", "Números de trabajo:", "12", ",", "8", ",", "15",
                                          "Operaciones básicas entre", "12", "y", "8", "Suma:", "20", "Resta:", "4"]
        }
    
    def list_available_tests(self):
        """Muestra los archivos de prueba disponibles"""
        print("📋 ARCHIVOS DE PRUEBA DISPONIBLES:")
        print("=" * 50)
        
        if not os.path.exists(self.tests_folder):
            print(f"❌ La carpeta '{self.tests_folder}' no existe!")
            return []
        
        available = []
        sorted_files = sorted(self.test_definitions.keys(), key=lambda x: int(x.split('_')[0]))
        
        for i, filename in enumerate(sorted_files, 1):
            file_path = os.path.join(self.tests_folder, filename)
            if os.path.exists(file_path):
                print(f"{i:2}. {filename}")
                available.append(filename)
            else:
                print(f"{i:2}. {filename} ❌ (no encontrado)")
        
        return available
    
    def select_test(self, available_tests):
        """Permite al usuario seleccionar una prueba"""
        while True:
            try:
                choice = input(f"\n🔍 Selecciona un archivo (1-{len(available_tests)}) o 'q' para salir: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(available_tests):
                    return available_tests[index]
                else:
                    print(f"❌ Número inválido. Debe ser entre 1 y {len(available_tests)}")
            
            except ValueError:
                print("❌ Por favor ingresa un número válido o 'q' para salir")
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                return None
    
    def run_test(self, filename):
        """Ejecuta una prueba específica y muestra solo los outputs"""
        file_path = os.path.join(self.tests_folder, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {filename}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"❌ Error leyendo archivo: {str(e)}")
            return
        
        print(f"\n🚀 EJECUTANDO: {filename}")
        print("=" * 60)
        
        captured_output = io.StringIO()
        captured_error = io.StringIO()
        
        try:
            with redirect_stdout(captured_output), redirect_stderr(captured_error):
                result = execute_program(code)
            
            output_lines = captured_output.getvalue().strip()
            error_lines = captured_error.getvalue().strip()
            
            clean_output = []
            if output_lines:
                for line in output_lines.split('\n'):
                    if line.startswith('OUTPUT: '):
                        clean_output.append(line.replace('OUTPUT: ', ''))
            
            print("📤 SALIDA DEL PROGRAMA:")
            print("-" * 30)
            if clean_output:
                for line in clean_output:
                    print(line)
            else:
                print("(Sin salida)")
            
            expected = self.test_definitions.get(filename, [])
            success = self._verify_output(' '.join(clean_output), expected)
            
            print("\n" + "-" * 30)
            if success:
                print("✅ RESULTADO: FUNCIONÓ CORRECTAMENTE")
            else:
                print("❌ RESULTADO: NO FUNCIONÓ COMO SE ESPERABA")
                print("\n🎯 Se esperaba encontrar:")
                for exp in expected[:5]:  
                    print(f"  - {exp}")
                if len(expected) > 5:
                    print(f"  ... y {len(expected) - 5} más")
            
            self._save_result(filename, clean_output, success)
            
        except Exception as e:
            print(f"❌ ERROR EN EJECUCIÓN: {str(e)}")
            self._save_result(filename, [f"ERROR: {str(e)}"], False)
    
    def _verify_output(self, output, expected_outputs):
        """Verifica si la salida contiene los elementos esperados"""
        if not output:
            return len(expected_outputs) == 0
        
        output_lower = output.lower()
        
        for expected in expected_outputs:
            expected_lower = str(expected).lower()
            if expected_lower not in output_lower:
                return False
        return True
    
    def _save_result(self, filename, output_lines, success):
        """Guarda el resultado en un archivo"""
        results_folder = "ResultadosTests"
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        
        result_filename = os.path.join(results_folder, f"resultado_{filename.replace('.txt', '')}.txt")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(result_filename, 'w', encoding='utf-8') as f:
            f.write(f"RESULTADO DE PRUEBA: {filename}\n")
            f.write(f"FECHA: {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("SALIDA DEL PROGRAMA:\n")
            f.write("-" * 20 + "\n")
            if output_lines:
                for line in output_lines:
                    f.write(line + "\n")
            else:
                f.write("(Sin salida)\n")
            
            f.write("\n" + "-" * 20 + "\n")
            f.write(f"RESULTADO: {'FUNCIONÓ CORRECTAMENTE' if success else 'NO FUNCIONÓ COMO SE ESPERABA'}\n")
        
        print(f"💾 Resultado guardado en: {results_folder}/{os.path.basename(result_filename)}")

def main():
    print("🔧 EVALUADOR SIMPLE DE ARCHIVOS")
    print("=" * 50)
    
    runner = SimpleTestRunner()
    
    while True:
        available_tests = runner.list_available_tests()
        
        if not available_tests:
            print("\n❌ No hay archivos de prueba disponibles")
            break
        
        selected_file = runner.select_test(available_tests)
        
        if selected_file is None:
            print("\n👋 ¡Hasta luego!")
            break
        
        runner.run_test(selected_file)
        
        while True:
            continue_choice = input(f"\n🔄 ¿Quieres probar otro archivo? (s/n): ").strip().lower()
            if continue_choice in ['s', 'si', 'y', 'yes']:
                break
            elif continue_choice in ['n', 'no']:
                print("\n👋 ¡Hasta luego!")
                return
            else:
                print("❌ Por favor responde 's' para sí o 'n' para no")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()