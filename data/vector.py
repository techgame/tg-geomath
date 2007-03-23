##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import numpy
from numpy import ndarray as _ndarray, array as _array

from .dataDescriptors import dataProperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class VectorItemProperty(object):
    key = None
    def __init__(self, key):
        self.key = key

    def __get__(self, obj, objKlass=None):
        if obj is None:
            return self
        return obj._data[self.key]
    def __set__(self, obj, value):
        obj._data[self.key] = value

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Vector(_ndarray):
    """Uniform data vector"""

    __array_priority__ = 20.0
    default_dtype = numpy.float

    @classmethod
    def __ndnew__(klass, shape, dtype=None, buffer=None, offset=0, strides=None, order='C'):
        """Semantics of numpy.ndarray.__new__"""
        if dtype is None: 
            dtype = klass.default_dtype
        return _ndarray.__new__(klass, shape, dtype, buffer, offset, strides, order)

    def __nonzero__(self):
        return self.size != 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def fromData(klass, data, dtype=None, copy=True, order='C', subok=True, ndmin=1):
        """Semantics of numpy.array"""
        self = _array(data, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=ndmin)
        self = self.view(klass)
        return self

    @classmethod
    def fromShape(klass, shape, dtype=None):
        return klass.__ndnew__(shape, dtype)

    @classmethod
    def fromBuffer(klass, buffer, offset=0, shape=-1, dtype=None, strides=None, order='C'):
        return klass.__ndnew__(shape, dtype, buffer, offset, strides, order)

    _as_parameter_ = property(lambda self: self.ctypes._data)
Vector.property = classmethod(dataProperty)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def vecZeros(shape, dtype=None):
    r = Vector.fromShape(shape, dtype)
    r.fill(0)
    return r

def vecOnes(shape, dtype=None):
    r = Vector.fromShape(shape, dtype)
    r.fill(1)
    return r

def vector(data, dtype=None, copy=True, order='C', subok=True, ndmin=1):
    return Vector.fromData(data, dtype, copy, order, subok, ndmin)

def asVector(data, dtype=None, copy=False, order='C', subok=True, ndmin=1):
    return Vector.fromData(data, dtype, copy, order, subok, ndmin)

