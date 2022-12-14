##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

"""Symbols and symbolic operators

Useful for reviewing formulas in symbolic form.  Especially when crunched
through numpy.
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import numpy
from numpy import ndarray
import operator as opmodule

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

numbers = (int, long, float)

class SymbolicMathMixin(object):
    def __cmp__(self, other):
        return cmp(repr(self), repr(other))
    def __add__(self, other):
        if isinstance(other, ndarray):
            return vop2('+', self, other)
        if isinstance(other, numbers):
            if other == 0: return self
        return Operator('+', self, other)
    def __radd__(self, other):
        if isinstance(other, numbers):
            if other == 0: return self
        return Operator('+', other, self)

    def __sub__(self, other):
        if isinstance(other, ndarray):
            return vop2('-', self, other)
        if isinstance(other, numbers):
            if other == 0: return self
        return Operator('-', self, other)
    def __rsub__(self, other):
        if isinstance(other, numbers):
            if other == 0: return -self
        return Operator('-', other, self)

    def __mul__(self, other):
        if isinstance(other, ndarray):
            return vop2('*', self, other)
        if isinstance(other, numbers):
            if other == 0: return other
            elif other == 1: return self
            elif other == -1: return -self
        return Operator('*', self, other)
    def __rmul__(self, other):
        if isinstance(other, numbers):
            if other == 0: return other
            elif other == 1: return self
            elif other == -1: return -self
        return Operator('*', other, self)

    def __mod__(self, other):
        if isinstance(other, ndarray):
            return vop2('%', self, other)
        return Operator('%', self, other)
    def __rmod__(self, other):
        return Operator('%', other, self)

    def __divmod__(self, other):
        if isinstance(other, ndarray):
            return vop2('divmod', self, other)
        return Operator('divmod', self, other)
    def __rdivmod__(self, other):
        return Operator('divmod', other, self)

    def __div__(self, other):
        if isinstance(other, ndarray):
            return vop2('/', self, other)
        if isinstance(other, numbers):
            if other == 1: return self
        return Operator('/', self, other)
    def __rdiv__(self, other):
        if isinstance(other, numbers):
            if other == 0: return other
        return Operator('/', other, self)

    def __truediv__(self, other):
        if isinstance(other, ndarray):
            return vop2('/!', self, other)
        if isinstance(other, numbers):
            if other == 1: return self
        return Operator('/!', self, other)
    def __rtruediv__(self, other):
        if isinstance(other, numbers):
            if other == 0: return other
        return Operator('/!', other, self)

    def __floordiv__(self, other):
        if isinstance(other, ndarray):
            return vop2('//', self, other)
        return Operator('//', self, other)
    def __rfloordiv__(self, other):
        if isinstance(other, numbers):
            if other == 0: return other
        return Operator('//', other, self)

    def __pow__(self, other, *modulo):
        if isinstance(other, ndarray):
            if modulo:
                return vop3('pow', self, other, *modulo)
            return vop2('**', self, other)
        if isinstance(other, numbers):
            if other == 0: return 1
        if modulo:
            return Operator('pow', self, other, *modulo)
        return Operator('**', self, other)
    def __rpow__(self, other):
        return Operator('**', other, self)

    def __neg__(self):
        return Operator('-', self)
    def __pos__(self):
        return Operator('+', self)
    def __abs__(self):
        return Operator('abs', self)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Operator(SymbolicMathMixin):
    def __init__(self, op, *operands):
        self.op = op
        self.operands = operands

    def __repr__(self):
        return reprExpr(self)

    def append(self, *operands):
        return self.__class__(self.op, *(self.operands + operands))

    def accept(self, visitor):
        return visitor.visitOperator(self)

    def eval(self, values=(), **kwvalues):
        return evalExpr(self, values, **kwvalues)

def vop2(op, a, b):
    return ufunc_op2(Operator(op, a), b)

def ufunc_op2(opA, b):
    return opA.append(b)
ufunc_op2 = numpy.frompyfunc(ufunc_op2, 2, 1)

def vop3(op, a, b, c):
    return ufunc_op2(Operator(op, a), b, c)

def ufunc_op3(opA, b, c):
    return opA.append(b, c)
ufunc_op3 = numpy.frompyfunc(ufunc_op3, 3, 1)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Symbol(SymbolicMathMixin):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return reprExpr(self.name)

    def accept(self, visitor):
        return visitor.visitSymbol(self)

    def eval(self, values=(), **kwvalues):
        return evalExpr(self, values, **kwvalues)

class SymbolFactory(object):
    def __getattr__(self, name):
        return Symbol(name)
sym = SymbolFactory()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Expression Visitors
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PPExpression(object):
    def pprint(self, item):
        print self.visit(item)
    def visit(self, item):
        accept = getattr(item, 'accept', None)
        if accept is None:
            return self.visitBasic(item)
        else: return accept(self)
    __call__ = visit

    def visitBasic(self, item):
        if isinstance(item, (int, long, basestring, float, complex)):
            return str(item)
        if isinstance(item, numpy.ndarray):
            result = numpy.array([self.visit(e) for e in item.flat], 'object')
            result.shape = item.shape
            return str(result).replace('\n', '')

        return '[' + ', '.join(map(self.visit, item)) + ']'

    def visitSymbol(self, symbol):
        return symbol.name

    def visitOperator(self, operator):
        op = operator.op
        operands = [self.visit(opand) for opand in operator.operands]
        if op.isalpha():
            return '%s(%s)' % (op, ', '.join(operands))
        elif len(operands) > 1:
            return '('+(' %s '%op).join(operands)+')'
        else:
            return op + ''.join(operands)
ppExpr = PPExpression()
reprExpr = ppExpr.visit
pprintExpr = ppExpr.pprint

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ExprEvaluator(object):
    opTable = {
        ('+', 2): opmodule.add,
        ('-', 2): opmodule.sub,
        ('*', 2): opmodule.mul,
        ('%', 2): opmodule.mod,
        ('pow', 2): opmodule.pow,
        ('/', 2): opmodule.div,
        ('//', 2): opmodule.floordiv,
        ('/!', 2): opmodule.truediv,
        ('*', 2): opmodule.mul,

        ('**', 2): opmodule.pow,
        ('pow', 2): opmodule.pow,
        ('pow', 3): opmodule.pow,

        ('+', 1): opmodule.pos,
        ('-', 1): opmodule.neg,
        ('abs', 1): opmodule.abs,
    }

    def __init__(self, values=(), **kwvalues):
        self.values = dict(values)
        self.values.update(kwvalues)

    def update(self, values=(), **kwvalues):
        self.values.update(values)
        self.values.update(kwvalues)

    @classmethod
    def evaluate(klass, expr, values=(), **kwvalues):
        self = klass(values, **kwvalues)
        return self.visit(expr)

    def visit(self, item, **kwvalues):
        self.update(kwvalues)
        accept = getattr(item, 'accept', None)
        if accept is None:
            return self.visitBasic(item)
        else: 
            return accept(self)
    __call__ = visit

    def visitBasic(self, item):
        if isinstance(item, (int, long, basestring, float, complex)):
            return item
        if isinstance(item, numpy.ndarray):
            r = numpy.fromiter((self.visit(e) for e in item), 'object', item.size)
            r.shape = item.shape
            return r
        return map(self.visit, item)

    def visitSymbol(self, symbol):
        return self.values.get(symbol.name, symbol)

    def visitOperator(self, operator):
        operands = [self.visit(opand) for opand in operator.operands]
        opfn = self.opTable[operator.op, len(operands)]
        return opfn(*operands)
ExprEval = ExprEvaluator
evalExpr = ExprEval.evaluate

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    x1 = Symbol('x1')
    y1 = Symbol('y1')
    x2 = Symbol('x2')
    y2 = Symbol('y2')
    w = Symbol('w')
    h = Symbol('h')

    expr = w*h*x1/2
    print expr
    pprintExpr(expr)

