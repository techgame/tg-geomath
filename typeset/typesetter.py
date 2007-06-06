#!/usr/bin/env python
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
from .wrap import wrapModeMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TypeSetter(DataHostObject):
    offset = 0
    face = None
    kern = True
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

    def clear(self):
        self.text = u''
        self._rope = []

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    softspace = False
    def write(self, text, **kw):
        if kw: self.attr(kw.items())

        if not text:
            return 

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
    add = write

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    _wrapModes = wrapModeMap
    def wrap(self, size=None, wrapMode=None):
        text = self.text
        if not text: return []

        if wrapMode is None:
            wrapMode = self.wrapMode

        if not hasattr(wrapMode, 'wrapSlices'):
            if isinstance(wrapMode, basestring):
                wrapMode = wrapMode.lower()
            wrapMode = self._wrapModes[wrapMode]()

        sorts = self.sorts
        wrapSlices = wrapMode.wrapSlices(size, text, sorts['offset'])
        return text, sorts, wrapSlices

