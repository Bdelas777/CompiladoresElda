# semantic_cube.py
from enum import Enum, auto

class Type(Enum):
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING = auto()
    ERROR = auto()
    VOID = auto()

class Operation(Enum):
    PLUS = auto()      # +
    MINUS = auto()     # -
    MULTIPLY = auto()  # *
    DIVIDE = auto()    # /
    GREATER = auto()   # >
    LESS = auto()      # 
    NOT_EQUAL = auto() # !=
    ASSIGN = auto()    # =

# Cubo semántico implementado como un diccionario tridimensional
# [operando1][operando2][operación] = tipo_resultado
semantic_cube = {
    Type.INT: {
        Type.INT: {
            Operation.PLUS: Type.INT,
            Operation.MINUS: Type.INT,
            Operation.MULTIPLY: Type.INT,
            Operation.DIVIDE: Type.FLOAT,  
            Operation.GREATER: Type.BOOL,
            Operation.LESS: Type.BOOL,
            Operation.NOT_EQUAL: Type.BOOL,
            Operation.ASSIGN: Type.INT
        },
        Type.FLOAT: {
            Operation.PLUS: Type.FLOAT,
            Operation.MINUS: Type.FLOAT,
            Operation.MULTIPLY: Type.FLOAT,
            Operation.DIVIDE: Type.FLOAT,
            Operation.GREATER: Type.BOOL,
            Operation.LESS: Type.BOOL,
            Operation.NOT_EQUAL: Type.BOOL,
            Operation.ASSIGN: Type.FLOAT
        }
    },
    Type.FLOAT: {
        Type.INT: {
            Operation.PLUS: Type.FLOAT,
            Operation.MINUS: Type.FLOAT,
            Operation.MULTIPLY: Type.FLOAT,
            Operation.DIVIDE: Type.FLOAT,
            Operation.GREATER: Type.BOOL,
            Operation.LESS: Type.BOOL,
            Operation.NOT_EQUAL: Type.BOOL,
            Operation.ASSIGN: Type.FLOAT
        },
        Type.FLOAT: {
            Operation.PLUS: Type.FLOAT,
            Operation.MINUS: Type.FLOAT,
            Operation.MULTIPLY: Type.FLOAT,
            Operation.DIVIDE: Type.FLOAT,
            Operation.GREATER: Type.BOOL,
            Operation.LESS: Type.BOOL,
            Operation.NOT_EQUAL: Type.BOOL,
            Operation.ASSIGN: Type.FLOAT
        }
    },
    Type.BOOL: {
        Type.BOOL: {
            Operation.NOT_EQUAL: Type.BOOL,
            Operation.ASSIGN: Type.BOOL
        }
    },
    Type.STRING: {
        Type.STRING: {
            Operation.ASSIGN: Type.STRING
        }
    }
}

def get_result_type(left_type, right_type, operation):
    try:
        return semantic_cube[left_type][right_type][operation]
    except KeyError:
        return Type.ERROR