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

class TextBlock(object):
    def __init__(self, text, sorts, slice):
        self.text = text
        self.sorts = sorts
        self.slice = slice

    def __repr__(self):
        return '<%s [%04s:%04s]>' % (self.__class__.__name__, self.slice.start, self.slice.stop)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TypeSetter(DataHostObject):
    offset = 0
    face = None
    color = Color.property('#ff')
    TextBlock = TextBlock

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
    def write(self, text):
        self.add(text)

    def add(self, text, **kw):
        if kw: self.attr(kw.items())

        sorts = self.face.translate(text)

        advance = sorts['advance']
        offset = sorts['offset']
        offset[0] = self.offset
        numpy.add(offset[:-1], advance[:-1], offset[1:])
        self.offset = offset[-1] + advance[-1]

        sorts['color'] = self.color

        self.text += text
        self._rope.append(sorts)

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


    wrapper = None
    _wrapModes = wrapModeMap
    def wrap(self, size=None, wrapper=None):
        text = self.text
        if not text: return []

        if not hasattr(wrapper, 'wrapSlices'):
            if isinstance(wrapper, basestring):
                wrapper = wrapper.lower()
            wrapper = self._wrapModes[wrapper]()

        sorts = self.sorts
        wrapSlices = wrapper.wrapSlices(size, text, sorts['offset'])
        return (self.TextBlock(text[sl], sorts[sl], sl) for sl in wrapSlices)

