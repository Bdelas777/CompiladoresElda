# vm_example.py - Ejemplo de uso de la Máquina Virtual

# Importar los módulos necesarios (asumiendo que están en archivos separados)
from lex import lexer  # Tu lexer
from yacc import parse_program  # Tu parser
from virtual_machine import VirtualMachine  # Tu VM
from MemoryManager import MemoryManager

def run_program_example():
    """Ejemplo completo de ejecución de un programa en la máquina virtual"""
    
    # Programa de ejemplo en tu lenguaje
    program_code = '''
program ejemplo;
var
    a, b : int;
    x, y : float;

void sumar(num : int)
[
    var resultado : int;
    {
        resultado = num + 10;
        print("El resultado es: ", resultado);
    }
];

main{
    a = 5;
    b = 3;
    x = 2.5;
    y = 1.5;
    
    print("Valores iniciales:");
    print("a = ", a);
    print("b = ", b);
    print("x = ", x);
    print("y = ", y);
    
    a = a + b;
    print("a + b = ", a);
    
    x = x * y;
    print("x * y = ", x);
    
    if (a > 5) {
        print("a es mayor que 5");
    } else {
        print("a no es mayor que 5");
    };
    
    sumar(a);
    
    print("Programa terminado");
}
end
    '''
    
    print("=" * 60)
    print("EJEMPLO DE USO DE LA MÁQUINA VIRTUAL")
    print("=" * 60)
    
    # Paso 1: Parsear el programa
    print("\n1. PARSEANDO EL PROGRAMA...")
    print("-" * 30)
    
    try:
        # Parsear el código y obtener los cuádruplos
        ast, errors = parse_program(program_code)
        
        if errors:
            print("ERRORES ENCONTRADOS:")
            for error in errors:
                print(f"  - {error}")
            return
        
        print("✓ Programa parseado exitosamente")
        
        # Obtener el analizador semántico y generador de cuádruplos del parser
        from yacc import semantic, quad_gen
        
        # Paso 2: Mostrar información de compilación
        print("\n2. INFORMACIÓN DE COMPILACIÓN...")
        print("-" * 30)
        
        print(f"Número de cuádruplos generados: {len(quad_gen.Quads)}")
        print(f"Variables globales: {len(semantic.global_vars)}")
        print(f"Funciones declaradas: {len(semantic.function_directory)}")
        
        # Mostrar directorio de funciones
        print("\nDirectorio de funciones:")
        for func_name, func_info in semantic.function_directory.items():
            start_addr = getattr(func_info, 'start_address', 'No definida')
            param_count = len(func_info.parameters) if hasattr(func_info, 'parameters') else 0
            print(f"  {func_name}: inicio={start_addr}, parámetros={param_count}")
        
        # Paso 3: Crear la máquina virtual
        print("\n3. CREANDO MÁQUINA VIRTUAL...")
        print("-" * 30)
        
        # Crear el administrador de memoria
        memory_manager = MemoryManager()
        
        # Crear la máquina virtual
        vm = VirtualMachine(memory_manager, quad_gen.Quads, semantic.function_directory)
        
        print("✓ Máquina virtual creada exitosamente")
        print(f"✓ Memoria inicializada")
        print(f"✓ {len(quad_gen.Quads)} cuádruplos cargados")
        
        # Paso 4: Ejecutar el programa
        print("\n4. EJECUTANDO PROGRAMA...")
        print("=" * 30)
        
        # Ejecutar el programa
        vm.execute()
        
        print("\n" + "=" * 30)
        print("EJECUCIÓN COMPLETADA")
        
    except Exception as e:
        print(f"ERROR durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

def run_debug_example():
    """Ejemplo de ejecución paso a paso para depuración"""
    
    # Programa más simple para depuración
    debug_code = '''
program debug;
var
    num1, num2, resultado : int;

main{
    num1 = 10;
    num2 = 5;
    resultado = num1 + num2;
    print("Resultado: ", resultado);
    
    if (resultado > 10) {
        print("El resultado es mayor que 10");
    } else {
        print("El resultado no es mayor que 10");
    };
}
end
    '''
    
    print("\n" + "=" * 60)
    print("EJEMPLO DE DEPURACIÓN PASO A PASO")
    print("=" * 60)
    
    try:
        # Parsear el programa
        ast, errors = parse_program(debug_code)
        
        if errors:
            print("ERRORES ENCONTRADOS:")
            for error in errors:
                print(f"  - {error}")
            return
        
        from yacc import semantic, quad_gen
        
        # Crear la máquina virtual
        memory_manager = MemoryManager()
        vm = VirtualMachine(memory_manager, quad_gen.Quads, semantic.function_directory)
        
        print("\nModo de depuración activado")
        print("Presiona Enter para ejecutar cada instrucción...")
        print("-" * 50)
        
        # Ejecutar paso a paso
        while vm.debug_step():
            continue
        
    except Exception as e:
        print(f"ERROR durante la depuración: {e}")
        import traceback
        traceback.print_exc()

def run_arithmetic_example():
    """Ejemplo enfocado en operaciones aritméticas"""
    
    arith_code = '''
program aritmetica;
var
    a, b, c, d : int;
    x, y, z : float;

main{
    a = 10;
    b = 3;
    c = a + b;
    d = a * b - c;
    
    print("Operaciones con enteros:");
    print("a = ", a);
    print("b = ", b);
    print("c = a + b = ", c);
    print("d = a * b - c = ", d);
    
    x = 5.5;
    y = 2.2;
    z = x / y;
    
    print("Operaciones con flotantes:");
    print("x = ", x);
    print("y = ", y);
    print("z = x / y = ", z);
}
end
    '''
    
    print("\n" + "=" * 60)
    print("EJEMPLO DE OPERACIONES ARITMÉTICAS")
    print("=" * 60)
    
    try:
        ast, errors = parse_program(arith_code)
        
        if errors:
            print("ERRORES:")
            for error in errors:
                print(f"  - {error}")
            return
        
        from yacc import semantic, quad_gen
        
        # Mostrar cuádruplos generados
        print("\nCuádruplos generados:")
        quad_gen.print_quads()
        
        # Ejecutar
        print("\nEjecutando programa...")
        memory_manager = MemoryManager()
        vm = VirtualMachine(memory_manager, quad_gen.Quads, semantic.function_directory)
        vm.execute()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def run_function_example():
    """Ejemplo enfocado en llamadas a funciones"""
    
    func_code = '''
program funciones;
var
    global_var : int;

void duplicar(numero : int)
[
    var doble : int;
    {
        doble = numero * 2;
        print("El doble de ", numero, " es ", doble);
    }
];

void saludar()
[
    {
        print("Hola desde la función saludar!");
        global_var = global_var + 1;
    }
];

main{
    global_var = 0;
    print("Valor inicial de global_var: ", global_var);
    
    saludar();
    print("Después de saludar, global_var: ", global_var);
    
    duplicar(5);
    duplicar(10);
    
    print("Programa terminado");
}
end
    '''
    
    print("\n" + "=" * 60)
    print("EJEMPLO DE LLAMADAS A FUNCIONES")
    print("=" * 60)
    
    try:
        ast, errors = parse_program(func_code)
        
        if errors:
            print("ERRORES:")
            for error in errors:
                print(f"  - {error}")
            return
        
        from yacc import semantic, quad_gen
        
        print("Información de funciones:")
        for func_name, func_info in semantic.function_directory.items():
            print(f"  {func_name}: {func_info}")
        
        print("\nEjecutando programa con funciones...")
        memory_manager = MemoryManager()
        vm = VirtualMachine(memory_manager, quad_gen.Quads, semantic.function_directory)
        vm.execute()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal que ejecuta todos los ejemplos"""
    
    print("EJEMPLOS DE USO DE LA MÁQUINA VIRTUAL")
    print("=" * 60)
    
    while True:
        print("\nSelecciona un ejemplo:")
        print("1. Ejemplo completo")
        print("2. Depuración paso a paso")
        print("3. Operaciones aritméticas")
        print("4. Llamadas a funciones")
        print("5. Salir")
        
        choice = input("\nIngresa tu opción (1-5): ").strip()
        
        if choice == '1':
            run_program_example()
        elif choice == '2':
            run_debug_example()
        elif choice == '3':
            run_arithmetic_example()
        elif choice == '4':
            run_function_example()
        elif choice == '5':
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, ingresa un número del 1 al 5.")

if __name__ == "__main__":
    main()