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

from operator import truediv

import numpy
from numpy import asarray

try:
    from TG.metaObserving import obproperty
except ImportError:
    def obproperty(obObjectFactory, *args, **kw):
        raise NotImplementedError("Could not import obproperty from TG.metaObserving")

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

def asBlend(host, rel, xfrm=_xfrmSize_f[:,None], xoff=_xfrmOff_f[:,None]):
    if rel is None: rel = host.at_rel_default
    return asarray(rel)*xfrm + xoff
def boxBlend(alpha, boxData):
    ar = asBlend(None, alpha)[:,None]
    return (boxData*ar).sum(-3)

def toAspect(size, aspect, nidx=0, didx=1):
    if isinstance(aspect, tuple):
        aspect, grow = aspect
    else: grow = None

    size = asarray(size)

    if aspect <= 0:
        return size

    if isinstance(grow, basestring):
        if grow == 'w':
            size[..., nidx] = aspect * size[..., didx]
            return size

        elif grow == 'h':
            size[..., didx] = aspect * size[..., nidx]
            return size

        else:
            raise RuntimeError('Unknown grow constant %r' % (grow,))

    acurrent = truediv(size[nidx], size[didx])
    if bool(grow) ^ (aspect > acurrent):
        # new h is greater than old h
        size[..., didx] = size[nidx] / aspect
    else:
        # new w is greater than old w
        size[..., nidx] = aspect * size[..., didx]
    return size


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Box accessors
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
        obj._data_changed_

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AtSyntax(object):
    def __init__(self, box):
        self.box = box
    def __getitem__(self, key):
        box = self.box
        if isinstance(key, slice):
            if key.step is not None:
                raise ValueError("At syntax does not support slice step value")

            rsize0 = key.start
            rsize1 = key.stop
            if rsize0 is None: 
                rsize0 = 0
            if rsize1 is None: 
                rsize1 = 1

            return box.size * (rsize1-rsize0)
        else:
            return box.atPos(key)
    def __setitem__(self, key, value):
        box = self.box
        if isinstance(key, slice):
            if key.step is not None:
                raise ValueError("At syntax does not support slice step value")

            rsize0 = key.start
            rsize1 = key.stop
            if rsize0 is None: 
                rsize0 = 0
            if rsize1 is None: 
                rsize1 = 1

            idrsize = 1./(rsize1-rsize0)

            value = idrsize*asarray(value)
            box.setSize(value, 0.5*(rsize1+rsize0))
        else:
            box.atPosSet(key, value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlendAtSyntax(object):
    _boxBlendData = staticmethod(boxBlend)
    def __init__(self, box):
        if not box.isBoxVector():
            raise ValueError("blendAt syntax only works for Box Vectors")
        self.box = box
    def __getitem__(self, alpha):
        box = self.box

        idx0, ialpha = divmod(alpha, 1)
        boxData = box._data[..., idx0:idx0+2, :, :]
        return box.fromData(self._boxBlendData(ialpha, boxData))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Box class -- the subject of the module
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Box(object):
    at_rel_default = 0 # our default relative should be p0... could be .5, or 1, or something more esoteric
    dtype_default = numpy.float

    DataFactory = lambda self, dtype: numpy.zeros((2,2), dtype)
    _asDataArray = staticmethod(asarray)
    _data = None
    _data_changed_ = None

    def __init__(self, data=None, p1=None, dtype=None):
        if dtype is None: 
            dtype = getattr(data, 'dtype', self.dtype_default)

        if data is None:
            data = self.DataFactory(dtype)

        else:
            if p1 is not None:
                data = [data, p1]
            elif numpy.ndim(data) == 1:
                data = [numpy.zeros_like(data), data]

            data = self._asDataArray(data, dtype)
            if data.shape[-2] != 2:
                raise ValueError("Box requires data.shape[-2] == 2.  Data.shape is %r" % (data.shape,))

        self._data = data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def repr(self, prefix=''):
        leading = '<%s ' % (self.__class__.__name__,)
        return leading + numpy.array2string(self._data, prefix=prefix+' '*len(leading))
    def __repr__(self):
        return self.repr()
    def __str__(self):
        return str(self._data)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Instance construction
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    @classmethod
    def fromSize(klass, size, aspect=None, dtype=None):
        if dtype is None: dtype = klass.dtype_default

        if aspect is not None:
            size = klass.toAspect(size, aspect)

        data = klass._asDataArray([numpy.zeros_like(size), size], dtype)
        return klass.fromData(data)

    @classmethod
    def fromPosSize(klass, pos, size, aspect=None, dtype=None):
        if dtype is None: dtype = klass.dtype_default

        if aspect is not None:
            size = klass.toAspect(size, aspect)

        data = klass._asDataArray([pos, size], dtype)
        data[1] += data[0]
        return klass.fromData(data)

    @classmethod
    def fromCorners(klass, p0, p1, dtype=None):
        if dtype is None: dtype = klass.dtype_default
        data = klass._asDataArray([p0, p1], dtype)
        return klass.fromData(data)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Data access descriptors
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    p0 = BoxItemProperty(numpy.s_[..., 0, :])
    p1 = BoxItemProperty(numpy.s_[..., 1, :])

    pv = BoxItemProperty(numpy.s_[...,])
    xv = BoxItemProperty(numpy.s_[..., 0])
    yv = BoxItemProperty(numpy.s_[..., 1])
    zv = BoxItemProperty(numpy.s_[..., 2])

    left = BoxItemProperty(numpy.s_[..., 0, 0])
    bottom = BoxItemProperty(numpy.s_[..., 0, 1])
    near = BoxItemProperty(numpy.s_[..., 0, 2])

    right = BoxItemProperty(numpy.s_[..., 1, 0])
    top = BoxItemProperty(numpy.s_[..., 1, 1])
    far = BoxItemProperty(numpy.s_[..., 1, 2])

    # aliases
    pos = p0
    corner = p1
    x0 = l = left
    y0 = t = top
    z0 = near

    x1 = r = right
    y1 = b = bottom
    z1 = far

    def getDtype(self):
        return self._data.dtype
    def setDtype(self, dtype):
        self._data.dtype = dtype
        self._data_changed_
    dtype = property(getDtype, setDtype)

    def getShape(self):
        return self._data.shape
    def setShape(self, shape):
        self._data.shape = shape
        self._data_changed_
    shape = property(getShape, setShape)

    def getNdim(self):
        return self._data.ndim
    ndim = property(getNdim)

    def isBoxVector(self):
        return self.ndim > 2

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Box methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def inset(self, delta, xfrm=-_xfrmSize):
        self.offset(xfrm*delta)
    def offset(self, delta):
        self._data += delta
        self._data_changed_

    def scaleAt(self, scale, at=None, sidx=Ellipsis):
        self._data[sidx] =  self.posForSizeAt(at, self.size*scale, sidx)
        self._data_changed_

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @property
    def blendAt(self):
        return BlendAtSyntax(self)

    _boxBlendData = staticmethod(boxBlend)
    def blend(self, alpha, other):
        data = self._boxBlendData(alpha, [self._data, other._data])
        return self.fromData(data)

    @property
    def at(self):
        return AtSyntax(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _asBlend = asBlend

    def atPos(self, rel=None):
        ar = self._asBlend(rel)
        return (self._data*ar).sum(-2)
    def atPosSet(self, rel, value):
        ar = self._asBlend(rel)
        data = self._data
        data[:] += -(data*ar).sum(-2) + value

    def posForSizeAt(self, rel, size=None, sidx=Ellipsis, xfrm=-_xfrmSize):
        ar = self._asBlend(rel)
        v = (self._data[sidx]*ar).sum(-2) + xfrm*(ar*size)
        v.sort(-2)
        return v

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getSize(self, xfrm=_xfrmSize):
        return (self._data*xfrm).sum(-2)
    def setSize(self, size, at=None, sidx=Ellipsis):
        self._data[sidx] = self.posForSizeAt(at, size, sidx)
        self._data_changed_
    size = property(getSize, setSize)

    def getWidth(self, xfrm=_xfrmSize, sidx=numpy.s_[...,0,None]):
        return (self._data[sidx]*xfrm).sum(-2)
    def setWidth(self, size, at=None, sidx=numpy.s_[...,0,None]):
        self._data[sidx] = self.posForSizeAt(at, size, sidx)
        self._data_changed_
    w = width = property(getWidth, setWidth)

    def getHeight(self, xfrm=_xfrmSize, sidx=numpy.s_[...,1,None]):
        return (self._data[sidx]*xfrm).sum(-2)
    def setHeight(self, size, at=None, sidx=numpy.s_[...,1,None]):
        self._data[sidx] = self.posForSizeAt(at, size, sidx)
        self._data_changed_
    h = height = property(getHeight, setHeight)

    def getDepth(self, xfrm=_xfrmSize, sidx=numpy.s_[...,2,None]):
        return (self._data[sidx]*xfrm).sum(-2)
    def setDepth(self, size, at=None, sidx=numpy.s_[...,2,None]):
        self._data[sidx] = self.posForSizeAt(at, size, sidx)
        self._data_changed_
    d = depth = property(getDepth, setDepth)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getAspect(self, nidx=0, didx=1):
        size = self.getSize()
        return truediv(size[..., nidx], size[..., didx])
    def setAspect(self, aspect, at=None, ndix=0, didx=1):
        asize = self.toAspect(self.size, aspect, nidx, didx)
        return self.setSize(asize, at)
    aspect = property(getAspect, setAspect)

    def sizeInAspect(self, aspect, ndix=0, didx=1):
        return self.toAspect(self.size, aspect, nidx, didx)
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

    def __getitem__(self, key): 
        r = self._data[key]
        if r.ndim >= 2:
            r = self.fromData(r)
        return r
    def __setitem__(self, key, value): 
        self._data[key] = value
        self._data_changed_

    def __add__(self, other): return self._data.__add__(other)
    def __radd__(self, other): return self._data.__radd__(other)
    def __iadd__(self, other): self._data.__iadd__(other); self._data_changed_; return self

    def __sub__(self, other): return self._data.__sub__(other)
    def __rsub__(self, other): return self._data.__rsub__(other)
    def __isub__(self, other): self._data.__isub__(other); self._data_changed_; return self

    def __mod__(self, other): return self._data.__mod__(other)
    def __rmod__(self, other): return self._data.__rmod__(other)
    def __imod__(self, other): self._data.__imod__(other); self._data_changed_; return self

    def __mul__(self, other): return self._data.__mul__(other)
    def __rmul__(self, other): return self._data.__rmul__(other)
    def __imul__(self, other): self._data.__imul__(other); self._data_changed_; return self

    def __div__(self, other): return self._data.__div__(other)
    def __rdiv__(self, other): return self._data.__rdiv__(other)
    def __idiv__(self, other): self._data.__idiv__(other); self._data_changed_; return self

    def __truediv__(self, other): return self._data.__truediv__(other)
    def __rtruediv__(self, other): return self._data.__rtruediv__(other)
    def __itruediv__(self, other): self._data.__itruediv__(other); self._data_changed_; return self

    def __floordiv__(self, other): return self._data.__floordiv__(other)
    def __rfloordiv__(self, other): return self._data.__rfloordiv__(other)
    def __ifloordiv__(self, other): self._data.__ifloordiv__(other); self._data_changed_; return self

    def __pow__(self, other, *modulo):  return self._data.__pow__(other, *modulo)
    def __rpow__(self, other, *modulo):  return self._data.__rpow__(other)
    def __ipow__(self, other, *modulo):  self._data.__ipow__(other); self._data_changed_; return self

    def __neg__(self, other, *modulo):  return self._data.__neg__(other)
    def __pos__(self, other, *modulo):  return self._data.__pos__(other)
    def __abs__(self, other, *modulo):  return self._data.__abs__(other)

Box.property = obproperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CenterBox(Box):
    at_rel_default = 0.5

