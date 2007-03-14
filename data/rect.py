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

class Rect(object):
    _dtype = numpy.dtype('2f')

    def __init__(self, rect=None, dtype=None, copy=True):
        if dtype is not None:
            self._dtype = numpy.dtype(dtype)
        self._posSize = numpy.zeros(2, self._dtype)
        self._pos = self._posSize[0, :]
        self._size = self._posSize[1, :]

        if rect is None:
            self.pos = [0, 0]
            self.size = [0, 0]

        elif isinstance(rect, Rect):
            if copy:
                self.copyFrom(rect, dtype)
            else:
                self._pos = rect.pos
                self._size = rect.size

        else:
            self.pos, self.size = rect

    @classmethod
    def new(klass, dtype=None):
        self = klass.__new__(klass)
        if dtype is not None:
            self._dtype = numpy.dtype(dtype)
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _pos = None
    def getPos(self):
        return self._pos
    def setPos(self, pos):
        self._pos[:] = pos
    pos = property(getPos, setPos)

    _size = None
    def getSize(self):
        return self._size
    def setSize(self, size):
        self._size[:] = size
    size = property(getSize, setSize)

    def getDtype(self):
        return self._dtype
    def setDtype(self, dtype):
        dtype = numpy.dtype(dtype)
        self._pos = self._pos.astype(dtype)
        self._size = self._size.astype(dtype)
        self._dtype = dtype
    dtype = property(getDtype, setDtype)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __repr__(self):
        name = self.__class__.__name__
        pos = self.pos.tolist()
        size = self.size.tolist()
        return '%s(%s, %s)' % (name, pos, size)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def tolist(self):
        return self.pos.tolist() + self.size.tolist()

    def astype(self, dtype):
        return self.copy(dtype)

    def __copy__(self):
        return self.copy()

    def copy(self, dtype=None):
        return self.new().copyFrom(self, dtype)

    def copyFrom(self, other, dtype=None):
        self._pos = other.pos.copy()
        self._size = other.size.copy()

        if dtype is not None:
            self.dtype = dtype
        return self

    #~ setters and construction methods ~~~~~~~~~~~~~~~~~

    def setRect(self, rect, aspect=None, align=None, dtype=None):
        self._pos[:] = rect.pos
        self._size[:] = rect.size
        self.setAspect(aspect, align)
        return self

    @classmethod
    def fromRect(klass, rect, aspect=None, align=None, dtype=None):
        self = klass(rect, dtype)
        self.setAspect(aspect, align)
        return self

    @classmethod
    def fromSize(klass, size, aspect=None, align=None, dtype=None):
        self = klass(None, dtype)
        self.setSize(size, aspect, align)
        return self

    @classmethod
    def fromPosSize(klass, pos, size, aspect=None, align=None, dtype=None):
        self = klass(None, dtype)
        self.setPosSize(pos, size, aspect, align)
        return self

    def setPosSize(self, pos, size, aspect=None, align=None, grow=False):
        self._pos[:] = pos
        self.setSize(size, aspect, align, grow)
        return self

    @classmethod
    def fromCorners(klass, p0, p1, dtype=None):
        self = klass(None, dtype)
        self.setCorners(p0, p1)
        return self

    def setCorners(self, p0, p1):
        pv = vstack([p0, p1])
        p0 = pv.min(0); p1 = pv.max(0)
        return self.setPosSize(p0, p1-p0)

    def centerIn(self, other): 
        return self.alignIn(.5, other)
    def alignIn(self, align, other):
        if isinstance(other, Rect):
            self._pos[:] = other.pos + align*(other.size-self._size)
        else: 
            self._pos[:] += align*(other-self._size)
        return self

    def getCorner(self):
        return self._pos + self._size
    def setCorner(self, value):
        self._size = value - self._pos
    corner = property(getCorner, setCorner)
    
    def setSize(self, size, aspect=None, align=None, grow=False):
        self._size[:] = size
        if aspect is not None: 
            return self.setAspect(aspect, align, grow)
        return self
    def sizeAs(self, aspect):
        return self.toAspect(self._size.copy(), aspect)
    
    def growSize(self, size):
        self._size[:] = max(self._size, size)
    def shrinkSize(self, size):
        self._size[:] = min(self._size, size)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def unionCorners(klass, *args):
        rectItems = []
        for a in args:
            if isinstance(a, Rect):
                rectItems.append(a)
            else: rectItems.extend(a)

        if rectItems:
            pos = numpy.min([r.pos for r in rectItems], 0)
            corner = numpy.max([r.corner for r in rectItems], 0)
            return (pos, corner)

    def union(self, rectItems):
        p0p1 = self.unionCorners(self, rectItems)
        if p0p1 is not None:
            p0, p1 = p0p1
            self.setPosSize(p0, p1-p0)
        return self

    @classmethod
    def fromUnion(klass, rectItems):
        p0p1 = klass.unionCorners(rectItems)
        if p0p1 is not None:
            p0, p1 = p0p1
            return klass.fromPosSize(p0, p1-p0)

        return klass()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getAspect(self):
        s = self._size[0:2].astype(float)
        return s[0]/s[1]
    def setAspect(self, aspect, align=None, grow=False):
        if aspect is None: 
            return self

        if align is None:
            self.toAspect(self._size, aspect, grow)
            return self

        size = self._size.copy()
        self.toAspect(self._size, aspect, grow)
        return self.alignIn(align, size)
    aspect = property(getAspect, setAspect)

    toAspect = staticmethod(toAspect)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Named accessors
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sizeAt(self, align):
        return align*self._size

    def posAt(self, align):
        return self._pos + align*self._size
    at = posAt
    __getitem__ = posAt

    def setPosAt(self, align, value):
        self._pos[:] = (value - align*self._size)
        return self._pos
    __setitem__ = setPosAt

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getWidth(self): return self._size[0]
    def setWidth(self, width): self._size[0] = max(0, width)
    width = property(getWidth, setWidth)

    def getHeight(self): return self._size[1]
    def setHeight(self, height): self._size[1] = max(0, height)
    height = property(getHeight, setHeight)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getLeft(self): return self._pos[0]
    def setLeft(self, left): self._pos[0] = left
    left = property(getLeft, setLeft)

    def getBottom(self): return self._pos[1]
    def setBottom(self, bottom): self._pos[1] = bottom
    bottom = property(getBottom, setBottom)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getRight(self): return self._pos[0] + self._size[0]
    def setRight(self, right): self._pos[0] = right - self._size[0]
    right = property(getRight, setRight)

    def getTop(self): return self._pos[1] + self._size[1]
    def setTop(self, top): self._pos[1] = top - self._size[1]
    top = property(getTop, setTop)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Recti(Rect):
    _dtype = numpy.dtype('2i')

class Rectf(Rect):
    _dtype = numpy.dtype('2f')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = ['Rect', 'Recti', 'Rectf', 'toAspect']

