'''
  program operaciones_basicas;
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
end
'''

# Respuestas: 11,16,3.5,10,17,12,-6


'''
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
'''

# Respuestas: el primero es 15, el segundo es x es mayor o igual que 10 y el segundo es x es mayor o igual que 10

'''
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
        '''
# Respuestas: Iteración 1 suma 1, Iteración 2 suma 3, Iteración 3 suma 6, Iteración 4 suma 10, Suma final: 10

'''
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
        '''
# Respuestas: La suma es 11, El producto es 24, La suma es 12, El producto es 60


'''
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
'''

#Respuesta flotante: 8.5