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
from numpy import asarray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Transforms used in Box object
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_xfrmSize = numpy.array([[-1],[1]], 'b')
_xfrmSize_f = numpy.array([-1,1], 'f')
_xfrmOff_f = numpy.array([1,0], 'f')

xfrmQuads = numpy.array([
        [1,1,0,0],
        [0,1,1,0],
        [0,0,1,1],
        [1,0,0,1]], 'b').reshape((-1,2,2))
xfrmTriStrip = numpy.array([
        [1,0,0,1],
        [1,1,0,0],
        [0,0,1,1],
        [0,1,1,0]], 'b').reshape((-1,2,2))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def asblend(host, rel, xfrm=_xfrmSize_f[:,None], xoff=_xfrmOff_f[:,None]):
    if rel is None: rel = host.blend_default
    return asarray(rel)*xfrm + xoff

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
        return obj._data[self.key]
    def __set__(self, obj, value):
        obj._data[self.key] = value

class AtSyntax(object):
    def __init__(self, box):
        self.box = box
    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise ValueError("At syntax does not support slice step value")
            #raise NotImplementedError('At slice syntax not yet defined')
            box = self.box

            rsize0 = key.start
            rsize1 = key.stop
            if rsize0 is None: 
                rsize0 = box.blend_default
            if rsize1 is None: 
                rsize1 = box.blend_default_stop

            return box.size * float(rsize1-rsize0)
        else:
            return self.box.atPos(key)
    def __setitem__(self, key, value):
        if isinstance(key, slice):
            if key.step is not None:
                raise ValueError("At syntax does not support slice step value")
            #raise NotImplementedError('At slice syntax not yet defined')
            box = self.box

            rsize0 = key.start
            rsize1 = key.stop
            if rsize0 is None: 
                rsize0 = box.blend_default
            if rsize1 is None: 
                rsize1 = box.blend_default_stop

            idrsize = 1./(rsize1-rsize0)

            value = idrsize*asarray(value)
            box.setSize(value, 0.5*(rsize1+rsize0))
        else:
            self.box.atPosSet(key, value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Box(object):
    DataFactory = lambda self: numpy.zeros((2,2), numpy.float)
    _data = None
    blend_default = 0 # our default relative should be p0... could be .5, or 1, or something more esoteric
    blend_default_stop = 1

    def __init__(self, data=None, dtype=None):
        if data is None:
            data = self.DataFactory()
        else:
            data = asarray(data, dtype)
            if data.shape[-2] != 2:
                raise ValueError("Box requires data.shape[-2] == 2.  Data.shape is %r" % (data.shape,))
        self._data = data
    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._data)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Instance construction
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newWith(klass, *args, **kw):
        return klass.__new__(klass, *args, **kw)
    @classmethod
    def new(klass):
        return klass.__new__(klass)

    @classmethod
    def fromData(klass, data):
        if data.shape[-2] != 2:
            raise ValueError("Box requires data.shape[-2] == 2.  Data.shape is %r" % (data.shape,))
        self = klass.new()
        self._data = data
        return self

    def copy(self):
        return self.fromData(self._data.copy())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Data access descriptors
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    p0 = BoxItemProperty(numpy.s_[..., 0, :])
    p1 = BoxItemProperty(numpy.s_[..., 1, :])

    xv = BoxItemProperty(numpy.s_[..., :, 0])
    yv = BoxItemProperty(numpy.s_[..., :, 1])
    zv = BoxItemProperty(numpy.s_[..., :, 2])

    left = BoxItemProperty(numpy.s_[..., 0, 0])
    bottom = BoxItemProperty(numpy.s_[..., 0, 1])
    near = BoxItemProperty(numpy.s_[..., 0, 2])

    right = BoxItemProperty(numpy.s_[..., 1, 0])
    top = BoxItemProperty(numpy.s_[..., 1, 1])
    far = BoxItemProperty(numpy.s_[..., 1, 2])

    # aliases
    x0 = l = left
    y0 = t = top
    z0 = near

    x1 = r = right
    y1 = b = bottom
    z1 = far

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Box methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def inset(self, delta, xfrm=-_xfrmSize):
        delta = xfrm*delta
        self.offset(delta)
    def offset(self, delta):
        self._data += delta

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    asblend = asblend

    @property
    def at(self):
        return AtSyntax(self)

    def atPos(self, rel=None):
        ar = self.asblend(rel)
        return (self._data*ar).sum(-2)
    def atPosSet(self, rel, value):
        ar = self.asblend(rel)
        data = self._data
        data[:] += -(data*ar).sum(-2) + value

    def sizeAt(self, rel, size=None, sidx=Ellipsis, xfrm=-_xfrmSize):
        ar = self.asblend(rel)
        v = (self._data[sidx]*ar).sum(-2) + xfrm*(ar*size)
        v.sort(-2)
        return v

    def getSize(self, xfrm=_xfrmSize):
        return (self._data*xfrm).sum(-2)
    def setSize(self, size, at=None, sidx=Ellipsis):
        self._data[sidx] = self.sizeAt(at, size, sidx)
    size = property(getSize)

    def getWidth(self, xfrm=_xfrmSize, sidx=numpy.s_[...,0,None]):
        return (self._data[sidx]*xfrm).sum(-2)
    def setWidth(self, size, at=None, sidx=numpy.s_[...,0,None]):
        self._data[sidx] = self.sizeAt(at, size, sidx)
    w = width = property(getWidth, setWidth)

    def getHeight(self, xfrm=_xfrmSize, sidx=numpy.s_[...,1,None]):
        return (self._data[sidx]*xfrm).sum(-2)
    def setHeight(self, size, at=None, sidx=numpy.s_[...,1,None]):
        self._data[sidx] = self.sizeAt(at, size, sidx)
    h = height = property(getHeight, setHeight)

    def getDepth(self, xfrm=_xfrmSize, sidx=numpy.s_[...,2,None]):
        return (self._data[sidx]*xfrm).sum(-2)
    def setDepth(self, size, at=None, sidx=numpy.s_[...,2,None]):
        self._data[sidx] = self.sizeAt(at, size, sidx)
    d = depth = property(getDepth, setDepth)

    def getAspect(self, nidx=0, didx=1):
        size = self.getSize().astype(float)
        return size[..., nidx]/size[..., didx]
    def setAspect(self, aspect, at=None, grow=False, ndix=0, didx=1):
        asize = self.toAspect(self.size, aspect, grow)
        return self.setSize(asize, at)
    aspect = property(getAspect, setAspect)

    toAspect = staticmethod(toAspect)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getGeoData(self):
        return self._data[..., None, :, :]
    geoData = property(getGeoData)

    def geoXfrm(self, xfrm=xfrmQuads):
        return (xfrm * self.getGeoData()).sum(-2)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Array and Numeric overrides 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __array__(self, dtype=None): 
        if dtype is not None:
            return self._data.astype(dtype)
        else: return self._data

    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self._data[key] = value

    def __add__(self, other): return self._data.__add__(other)
    def __radd__(self, other): return self._data.__radd__(other)
    def __iadd__(self, other): self._data.__iadd__(other); return self

    def __sub__(self, other): return self._data.__sub__(other)
    def __rsub__(self, other): return self._data.__rsub__(other)
    def __isub__(self, other): self._data.__isub__(other); return self

    def __mod__(self, other): return self._data.__mod__(other)
    def __rmod__(self, other): return self._data.__rmod__(other)
    def __imod__(self, other): self._data.__imod__(other); return self

    def __mul__(self, other): return self._data.__mul__(other)
    def __rmul__(self, other): return self._data.__rmul__(other)
    def __imul__(self, other): self._data.__imul__(other); return self

    def __div__(self, other): return self._data.__div__(other)
    def __rdiv__(self, other): return self._data.__rdiv__(other)
    def __idiv__(self, other): self._data.__idiv__(other); return self

    def __truediv__(self, other): return self._data.__truediv__(other)
    def __rtruediv__(self, other): return self._data.__rtruediv__(other)
    def __itruediv__(self, other): self._data.__itruediv__(other); return self

    def __floordiv__(self, other): return self._data.__floordiv__(other)
    def __rfloordiv__(self, other): return self._data.__rfloordiv__(other)
    def __ifloordiv__(self, other): self._data.__ifloordiv__(other); return self

    def __pow__(self, other, *modulo):  return self._data.__pow__(other, *modulo)
    def __rpow__(self, other, *modulo):  return self._data.__rpow__(other)
    def __ipow__(self, other, *modulo):  self._data.__ipow__(other); return self

    def __neg__(self, other, *modulo):  return self._data.__neg__(other)
    def __pos__(self, other, *modulo):  return self._data.__pos__(other)
    def __abs__(self, other, *modulo):  return self._data.__abs__(other)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    from TG.geomath.data.symbolic import sym, evalExpr

    bdata = numpy.array([[sym.l, sym.b], [sym.r, sym.t]])
    bdata1 = numpy.array([[sym.l1, sym.b1], [sym.r1, sym.t1]])

    box = Box.fromData(bdata)
    boxn = Box.fromData(numpy.array([bdata, bdata1]))

    print
    print box.p0, box.p1
    print ((box.l, box.b), (box.r, box.t))
    print box.size, '==', (box.w, box.h), '==', (box.width, box.height)

    print
    print boxn.atPos(sym.a)
    print box.atPos((sym.xa, sym.ya))
    print evalExpr(box.atPos((.2, .5)), 
            l=-10, r=10,b=10,t=20)
    print evalExpr(box.atPos(.5), 
            l=-10, r=10,b=10,t=20)

    print
    print boxn.atPos(sym.a)
    print boxn.atPos((sym.xa, sym.ya))
    print evalExpr(boxn.atPos((.2, .5)), 
            l=-10, r=10,b=10,t=20,
            l1=-100, r1=100,b1=100,t1=200,
            )

