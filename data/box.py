##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2006  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import numpy
from numpy import vstack

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def toAspect(size, aspect, grow=None):
    if grow is None and isinstance(aspect, tuple):
        aspect, grow = aspect

    if aspect <= 0:
        return size

    if isinstance(grow, basestring):
        if grow == 'w':
            size[0:1] = aspect * size[1:2]
            return size

        elif grow == 'h':
            size[1:2] = aspect * size[0:1]
            return size

        else:
            raise RuntimeError('Unknown grow constant %r' % (grow,))

    acurrent = float(size[0])/size[1]
    if bool(grow) ^ (aspect > acurrent):
        # new h is greater than old h
        size[1:2] = size[0:1] / aspect
    else:
        # new w is greater than old w
        size[0:1] = aspect * size[1:2]
    return size


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BoxItemProperty(object):
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
#~ Transforms used in Box object
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_xfrmSize = numpy.array([-1,1], 'b')

class Box(object):
    DataFactory = lambda self: numpy.zeros((2,2), numpy.float)
    _data = None

    def __init__(self):
        self._data = self.DataFactory()
    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._data)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __array__(self): return self._data

    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self._data[key] = value

    def __add__(self, other): return self._data.__add__(other)
    def __radd__(self, other): return self._data.__radd__(other)
    def __sub__(self, other): return self._data.__sub__(other)
    def __rsub__(self, other): return self._data.__rsub__(other)
    def __mul__(self, other): return self._data.__mul__(other)
    def __rmul__(self, other): return self._data.__rmul__(other)
    def __div__(self, other): return self._data.__div__(other)
    def __rdiv__(self, other): return self._data.__rdiv__(other)
    def __truediv__(self, other): return self._data.__truediv__(other)
    def __rtruediv__(self, other): return self._data.__rtruediv__(other)
    def __floordiv__(self, other): return self._data.__floordiv__(other)
    def __rfloordiv__(self, other): return self._data.__rfloordiv__(other)
    def __pow__(self, other, *modulo):  return self._data.__pow__(other, *modulo)
    def __rpow__(self, other, *modulo):  return self._data.__rpow__(other)
    def __neg__(self, other, *modulo):  return self._data.__neg__(other)
    def __pos__(self, other, *modulo):  return self._data.__pos__(other)
    def __abs__(self, other, *modulo):  return self._data.__abs__(other)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    p0 = BoxItemProperty(numpy.s_[..., 0, :])
    p1 = BoxItemProperty(numpy.s_[..., 1, :])

    l = left = BoxItemProperty(numpy.s_[..., 0, 0])
    b = bottom = BoxItemProperty(numpy.s_[..., 0, 1])
    r = right = BoxItemProperty(numpy.s_[..., 1, 0])
    t = top = BoxItemProperty(numpy.s_[..., 1, 1])

    @property
    def width(self, xfrm=_xfrmSize): 
        return (xfrm*self._data[:,0]).sum(-1)
    @property
    def height(self, xfrm=_xfrmSize): 
        return (xfrm*self._data[:,1]).sum(-1)
    @property
    def depth(self, xfrm=_xfrmSize): 
        return (xfrm*self._data[:,2]).sum(-1)
    @property
    def size(self, xfrm=_xfrmSize[numpy.newaxis]): 
        return (xfrm*self._data).sum(-1)

