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
from numpy import zeros, empty, recarray

from TG.geomath.data.color import Color, DataHostObject
from TG.geomath.data.vector import Vector, DataHostObject
from .wrap import wrapModeMap

from .textblock import TextBlock

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_alignmentReverse = {0.0: 'left', 0.5: 'center', 1.0: 'right'}
_alignmentLookup = {'left':0.0, 'center':0.5, 'right':1.0}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TypeSetter(DataHostObject):
    offset = 0
    face = None
    kern = False
    color = Color.property('#ff')

    def __init__(self, **kw):
        if kw: self.attr(kw.items())
        self.clear()

    def attr(self, *args, **kw):
        if kw:
            args += (kw.items(),)
        for attrs in args:
            for n, v in attrs:
                setattr(self, n, v)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _block = None
    def getBlock(self):
        if self._block is None:
            self.setBlock(TextBlock())
        return self._block
    def setBlock(self, block):
        self._block = block
    block = property(getBlock, setBlock)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    alignVector = Vector.property([0.0, 1.0])
    def getAlign(self, axis=0):
        aw = self.alignVector[axis]
        return _alignmentReverse.get(self._align, self._align)
    def setAlign(self, align, axis=0):
        aw = _alignmentLookup.get(align, None)
        if aw is None:
            aw = float(align)
        if self.alignVector[axis] != aw:
            self.flush()
            self.alignVector[axis] = aw
    align = property(getAlign, setAlign)

    def getVerticalAlign(self):
        return self.getAlign(1)
    def setVerticalAlign(self, align, axis=0):
        self.setAlign(align, 1)
    valign = verticalAlign = property(getVerticalAlign, setVerticalAlign)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    softspace = False
    def write(self, text, **kw):
        if kw: self.attr(kw.items())

        if not text:
            return 

        if not isinstance(text, unicode):
            text = unicode(text)

        face = self.face
        sorts = face.translate(text)

        advance = sorts['advance']
        offset = sorts['offset']
        if self.kern:
            face.kern(sorts, advance)

        offset[0] += self.offset
        numpy.add(offset[:-1], advance[:-1], offset[1:])
        self.offset = offset[-1] + advance[-1]

        sorts['color'] = self.color

        self.text += text
        self._rope.append(sorts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        self.text = u''
        self._rope = []

    def getSorts(self):
        if not self.text: 
            return None

        rope = self._rope
        if len(rope) > 1:
            result = numpy.concatenate(self._rope)
            rope = [result]
            self._rope = rope
        else: result = rope[0]
        return result
    sorts = property(getSorts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    wrapMode = None
    wrapSize = Vector.property([0,0])
    _wrapModes = wrapModeMap
    def wrap(self):
        text = self.text
        wrapMode = self.wrapMode
        wrapSize = self.wrapSize

        if not hasattr(wrapMode, 'wrapSlices'):
            if isinstance(wrapMode, basestring):
                wrapMode = wrapMode.lower()
            wrapMode = self._wrapModes[wrapMode]()

        sorts = self.sorts
        wrapSlices = wrapMode.wrapSlices(wrapSize, text, sorts['offset'])
        return text, sorts, wrapSlices

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def flush(self):
        return self.block.flush(self)
    def compile(self):
        return self.block.compile(self)

