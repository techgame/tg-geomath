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

from .dataDescriptors import dataProperty, DataHostObject

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
        return obj[self.key]
    def __set__(self, obj, value):
        obj[self.key] = value

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class _VectorIndexSyntaxBase(object):
    def __init__(self, vec):
        self.vec = vec
    def __repr__(self):
        return '<%s of %s>' % (self.__class__.__name__, self.vec.__class__.__name__)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Vector(_ndarray):
    """Uniform data vector"""

    __array_priority__ = 20.0
    default_dtype = numpy.float

    v0 = VectorItemProperty(numpy.s_[..., 0:1])
    v1 = VectorItemProperty(numpy.s_[..., 1:2])
    v2 = VectorItemProperty(numpy.s_[..., 2:3])
    v3 = VectorItemProperty(numpy.s_[..., 3:4])

    vd1 = VectorItemProperty(numpy.s_[..., 0:1])
    vd2 = VectorItemProperty(numpy.s_[..., 0:2])
    vd3 = VectorItemProperty(numpy.s_[..., 0:3])
    vd4 = VectorItemProperty(numpy.s_[..., 0:4])

    def __new__(klass, data, dtype=None, copy=True, order='C', subok=True, ndmin=1):
        """Semantics of vector()"""
        return klass.fromData(data, dtype, copy, order, subok, ndmin)
    def __init__(self, data, dtype=None, copy=True, order='C', subok=True, ndmin=1):
        pass

    @classmethod
    def __ndnew__(klass, shape, dtype=None, buffer=None, offset=0, strides=None, order='C'):
        """Semantics of numpy.ndarray.__new__"""
        if dtype is None: 
            dtype = klass.default_dtype
        return _ndarray.__new__(klass, shape, dtype, buffer, offset, strides, order)

    def __nonzero__(self):
        return self.size != 0

    def repr(self, prefix=''):
        leading = '<%s ' % (self.__class__.__name__,)
        return leading + numpy.array2string(self, prefix=prefix+' '*len(leading)) + '>'
    def __repr__(self):
        return self.repr()

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

