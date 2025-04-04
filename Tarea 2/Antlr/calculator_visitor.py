from antlr4 import *
from CalculatorLexer import CalculatorLexer
from CalculatorParser import CalculatorParser
from CalculatorVisitor import CalculatorVisitor

class CalculatorEvaluator(CalculatorVisitor):
    def visitExpr(self, ctx):
        result = self.visit(ctx.term(0))
        for i in range(len(ctx.term()) - 1):
            if ctx.PLUS(i):
                result += self.visit(ctx.term(i + 1))
            else:
                result -= self.visit(ctx.term(i + 1))
        return result
    
    def visitTerm(self, ctx):
        result = self.visit(ctx.factor(0))
        for i in range(len(ctx.factor()) - 1):
            if ctx.MUL(i):
                result *= self.visit(ctx.factor(i + 1))
            else:
                divisor = self.visit(ctx.factor(i + 1))
                if divisor == 0:
                    raise Exception("División por cero")
                result /= divisor
        return result
    
    def visitFactor(self, ctx):
        if ctx.NUMBER():
            return float(ctx.NUMBER().getText())
        else:
            return self.visit(ctx.expr())