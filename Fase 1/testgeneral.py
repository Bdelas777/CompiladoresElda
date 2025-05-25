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