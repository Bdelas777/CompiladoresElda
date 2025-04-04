from antlr4 import *
from CalculatorLexer import CalculatorLexer
from CalculatorParser import CalculatorParser
from calculator_visitor import CalculatorEvaluator

def main():
    while True:
        try:
            expression = input("Ingrese una expresión matemática (o 'salir' para terminar): ")
            if expression.lower() == 'salir':
                break
                
            # Crear el lexer
            lexer = CalculatorLexer(InputStream(expression))
            # Crear el stream de tokens
            stream = CommonTokenStream(lexer)
            # Crear el parser
            parser = CalculatorParser(stream)
            # Obtener el árbol de análisis
            tree = parser.expr()
            
            # Crear y usar el evaluador
            evaluator = CalculatorEvaluator()
            result = evaluator.visit(tree)
            
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()