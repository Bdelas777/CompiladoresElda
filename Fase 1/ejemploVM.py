# ejemplo_vm.py
from yacc import parse_program  # Importa tu parser

def ejemplo_basico():
    """Ejemplo básico con operaciones aritméticas"""
    codigo = '''
program ejemplo1;
var
    a, b : int;
    resultado : int;
main{
    a = 5;
    b = 3;
    resultado = a + b;
    print(resultado);
}
end
    '''
    
    print("=== EJEMPLO BÁSICO ===")
    print("Código fuente:")
    print(codigo)
    print("\n" + "="*50)
    
    # Parsear y ejecutar
    resultado, errores, vm = parse_program(codigo)
    
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    
    return vm

def ejemplo_operaciones():
    """Ejemplo con diferentes operaciones"""
    codigo = '''
program operaciones;
var
    x, y : int;
    a, b : float;
    temp : int;
main{
    x = 10;
    y = 4;
    a = 3.5;
    b = 2.0;
    
    temp = x + y;
    print("Suma:", temp);
    
    temp = x - y;
    print("Resta:", temp);
    
    temp = x * y;
    print("Multiplicacion:", temp);
    
    temp = x / y;
    print("Division:", temp);
}
end
    '''
    
    print("\n=== EJEMPLO CON OPERACIONES ===")
    print("Código fuente:")
    print(codigo)
    print("\n" + "="*50)
    
    resultado, errores, vm = parse_program(codigo)
    
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    
    return vm

def ejemplo_condicionales():
    """Ejemplo con if-else"""
    codigo = '''
program condicionales;
var
    x, y : int;
    mayor : int;
main{
    x = 15;
    y = 10;
    
    if (x > y) {
        mayor = x;
        print("x es mayor");
    } else {
        mayor = y;
        print("y es mayor");
    };
    
    print("El mayor es:", mayor);
}
end
    '''
    
    print("\n=== EJEMPLO CON CONDICIONALES ===")
    print("Código fuente:")
    print(codigo)
    print("\n" + "="*50)
    
    resultado, errores, vm = parse_program(codigo)
    
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    
    return vm

def ejemplo_while():
    """Ejemplo con ciclo while"""
    codigo = '''
program ciclos;
var
    contador : int;
    suma : int;
main{
    contador = 1;
    suma = 0;
    
    while (contador < 5) do {
        suma = suma + contador;
        print("Contador:", contador, "Suma:", suma);
        contador = contador + 1;
    };
    
    print("Suma final:", suma);
}
end
    '''
    
    print("\n=== EJEMPLO CON WHILE ===")
    print("Código fuente:")
    print(codigo)
    print("\n" + "="*50)
    
    resultado, errores, vm = parse_program(codigo)
    
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    
    return vm

def ejemplo_funciones():
    """Ejemplo con funciones"""
    codigo = '''
program funciones;
var
    numero : int;
    
void saludar(n : int)
[
    var local_var : int;
    {
        local_var = n * 2;
        print("Hola! El doble de", n, "es", local_var);
    }
];

main{
    numero = 7;
    print("Llamando a la funcion...");
    saludar(numero);
    print("Funcion terminada");
}
end
    '''
    
    print("\n=== EJEMPLO CON FUNCIONES ===")
    print("Código fuente:")
    print(codigo)
    print("\n" + "="*50)
    
    resultado, errores, vm = parse_program(codigo)
    
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    
    return vm

def ejemplo_completo():
    """Ejemplo más complejo combinando todo"""
    codigo = '''
program completo;
var
    x, y, resultado : int;
    promedio : float;
    
void calcular(a : int, b : int)
[
    var temp : int;
    {
        temp = a + b;
        print("La suma es:", temp);
        temp = a * b;
        print("El producto es:", temp);
    }
];

main{
    x = 8;
    y = 12;
    
    print("=== CALCULADORA SIMPLE ===");
    print("Numeros:", x, "y", y);
    
    calcular(x, y);
    
    resultado = x + y;
    promedio = resultado / 2;
    
    if (x > y) {
        print("x es mayor que y");
    } else {
        print("y es mayor o igual que x");
    };
    
    print("Resultado final:", resultado);
    print("Promedio:", promedio);
}
end
    '''
    
    print("\n=== EJEMPLO COMPLETO ===")
    print("Código fuente:")
    print(codigo)
    print("\n" + "="*50)
    
    resultado, errores, vm = parse_program(codigo)
    
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    
    return vm

# Función principal para ejecutar todos los ejemplos
def main():
    print("EJECUTANDO EJEMPLOS DE LA VIRTUAL MACHINE")
    print("="*70)
    
    # Ejecutar ejemplos uno por uno
    ejemplo_basico()
    ejemplo_operaciones()
    ejemplo_condicionales()
    ejemplo_while()
    ejemplo_funciones()
    ejemplo_completo()
    
    print("\n" + "="*70)
    print("TODOS LOS EJEMPLOS EJECUTADOS")

if __name__ == "__main__":
    main()