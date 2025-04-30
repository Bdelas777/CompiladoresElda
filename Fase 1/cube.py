# semantic_cube.py - Cubo Semántico para BabyDuck
# Definición de tipos disponibles en BabyDuck
INT = 'int'
FLOAT = 'float'
ERROR = 'error'

# Operadores aritméticos
PLUS = '+'
MINUS = '-'
MULT = '*'
DIV = '/'

# Operadores relacionales
GT = '>'
LT = '<'
NE = '!='
GE = '>='
LE = '<='

# Tabla de tipos resultantes para operaciones aritméticas y relacionales
semantic_cube = {
    # Operaciones aritméticas
    INT: {
        INT: {
            PLUS: INT,
            MINUS: INT,
            MULT: INT,
            DIV: FLOAT,  # División de enteros da float
            GT: INT,     # Operaciones relacionales dan resultado int (0/1 como booleano)
            LT: INT,
            NE: INT,
            GE: INT,
            LE: INT
        },
        FLOAT: {
            PLUS: FLOAT,
            MINUS: FLOAT,
            MULT: FLOAT,
            DIV: FLOAT,
            GT: INT,
            LT: INT,
            NE: INT,
            GE: INT,
            LE: INT
        }
    },
    FLOAT: {
        INT: {
            PLUS: FLOAT,
            MINUS: FLOAT,
            MULT: FLOAT,
            DIV: FLOAT,
            GT: INT,
            LT: INT,
            NE: INT,
            GE: INT,
            LE: INT
        },
        FLOAT: {
            PLUS: FLOAT,
            MINUS: FLOAT,
            MULT: FLOAT,
            DIV: FLOAT,
            GT: INT,
            LT: INT,
            NE: INT,
            GE: INT,
            LE: INT
        }
    }
}

def get_result_type(left_type, right_type, operator):
    """
    Consulta el cubo semántico para determinar el tipo resultante de una operación
    
    Args:
        left_type: Tipo del operando izquierdo
        right_type: Tipo del operando derecho
        operator: Operador de la operación
    
    Returns:
        Tipo resultante de la operación o ERROR si la operación no es válida
    """
    try:
        return semantic_cube[left_type][right_type][operator]
    except KeyError:
        return ERROR