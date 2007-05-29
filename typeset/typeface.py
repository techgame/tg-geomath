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
from numpy import resize, array, empty, zeros

from TG.freetype2.face import FreetypeFace, FreetypeException

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ArrayEntryPool(object):
    def __init__(self, dtype, blockCount=256):
        self.idx = 0
        self._blockCount = blockCount
        self.pool = empty(0, dtype)

    def addBlock(self, idx=0):
        pool = self.pool
        if len(pool) > 0:
            count = len(pool) + self._blockCount
            pool = resize(pool, count)
        else: pool = empty(self._blockCount, pool.dtype)

        self.pool = pool
        return idx, pool

    def __iter__(self):
        return self

    def next(self):
        i = self.idx
        pool = self.pool
        if i >= len(pool):
            i, pool = self.addBlock(i)
        self.idx = i+1
        return i, pool[i]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Glyph Dtype
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


dtype_sorts = numpy.dtype([
    ('glyphidx', 'L'), # offset: 0, +1*4
    ('typeface', 'object'), # offset: 4, +1*4
    ('hidx', 'L'), # offset: 8, +1*4
    ('size', 'h', (2,)), # offset: 12, +2*2

    ('advance', 'h', (2,)), # offset: 16, +2*2
    ('offset', 'l', (2,)), # offset: 20, +2*4
    ('color', 'B', (4,)), # offset: 28, +4*1
    ('quad', 'h', (4,2)), # offset: 32, +4*2*2

    # offset: 48, +0
    ])

class Typeface(dict):
    _vecTranslate = None

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._getFaceName())

    def _getFaceName(self):
        return None

    def translate(self, text):
        idxmap = map(self.__getitem__, unicode(text))
        return self.getSorts(idxmap)

    def __missing__(self, ordOrChar):
        if isinstance(ordOrChar, int):
            entry = self._loadChar(ordOrChar)
        else: 
            entry = self[ord(ordOrChar)]

        self[ordOrChar] = entry
        return entry

    def _loadChar(self, ordChar):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def loadAll(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def bitmapFor(self, sort):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    PoolFactory = ArrayEntryPool
    _sorts_dtype = dtype_sorts
    _arrPool = None

    def _createPool(self, total):
        self._arrPool = self.PoolFactory(self._sorts_dtype)

    def _nextEntry(self):
        return self._arrPool.next()

    def getSorts(self, idx=None):
        if idx is None:
            idx = slice(None, self._arrPool.idx)
        return self._arrPool.pool[idx]
    sorts = property(getSorts)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Freetype Typeface Implementation
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FTTypeface(Typeface):
    _boxToQuad = numpy.array([
            [[1,1],[0,0]],
            [[0,1],[1,0]],
            [[0,0],[1,1]],
            [[1,0],[0,1]]], 'l')

    def __init__(self, ftFace, size=None, dpi=72):
        if isinstance(ftFace, basestring):
            ftFace = FreetypeFace(ftFace)

        if size is not None:
            ftFace.setCharSize(size, dpi)

        self._ftFace = ftFace
        self._createPool(ftFace.numGlyphs)

    def _getFaceName(self):
        return self._ftFace._getInfoName()

    def _loadChar(self, ordChar):
        char = unichr(ordChar)
        ftGlyphSlot = self._ftFace.loadGlyph(char)
        return self._loadGlyph(ftGlyphSlot)

    def _loadGlyph(self, ftGlyphSlot):
        idx, entry = self._nextEntry()

        entry['typeface'] = self
        entry['hidx'] = hash((id(self), ftGlyphSlot.index))
        entry['glyphidx'] = ftGlyphSlot.index
        entry['advance'][:] = ftGlyphSlot.padvance
        entry['offset'][:] = 0
        entry['color'][:] = 0
        pbox = ftGlyphSlot.pbox
        entry['quad'][:] = (pbox * self._boxToQuad).sum(1)
        entry['size'][:] = (pbox[1] - pbox[0])
        return idx

    def loadAll(self):
        ftFace = self._ftFace
        for cc, gi in ftFace.iterAllChars(True):
            ftGlyphSlot = ftFace.loadGlyph(gi)
            idx = self._loadGlyph(ftGlyphSlot)
            self[ord(cc)] = idx

    def bitmapFor(self, sort):
        ftFace = self._ftFace
        gi = int(sort['glyphidx'])
        ftGlyphSlot = ftFace.loadGlyph(gi)
        ftGlyphSlot.render()
        return ftGlyphSlot.getBitmapArray()

