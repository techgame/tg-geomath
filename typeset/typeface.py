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
    ('glyphidx', 'L'),
    ('typeface', 'object'),
    ('hidx', 'L'),
    ('lineSize', 'h', (2,)),
    ('ascenders', 'h', (2,1)),

    ('advance', 'h', (1, 2)),
    ('offset', 'l', (1, 2)),
    ('color', 'B', (1, 4)),
    ('quad', 'l', (4, 2)),
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
    def kern(self, sorts, out):
        return None 

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
    lineSize = None
    ascenders = None

    def __init__(self, ftFace, size=None, dpi=72):
        if isinstance(ftFace, basestring):
            ftFace = FreetypeFace(ftFace)

        if size is not None:
            ftFace.setCharSize(size, dpi)

        self._ftFace = ftFace

        lh = ftFace.lineHeight >> 6
        if ftFace.isLayoutVertical():
            self.lineSize = numpy.array([lh,0], 'h')
        else: self.lineSize = numpy.array([0,lh], 'h')
        self.ascenders = numpy.array([[ftFace.lineAscender >> 6], [ftFace.lineDescender >> 6]], 'h')

        self._createPool(ftFace.numGlyphs)

    def kern(self, sorts, advance=None):
        if advance is None:
            advance = numpy.zeros((len(sorts), 1, 2), 'l')

        return self._ftFace.kernArray(sorts['glyphidx'], advance)

    def _getFaceName(self):
        return self._ftFace._getInfoName()

    def _loadChar(self, ordChar):
        char = unichr(ordChar)
        ftGlyphSlot = self._ftFace.loadGlyph(char)
        return self._loadGlyph(ftGlyphSlot, char)

    def _loadGlyph(self, ftGlyphSlot, char):
        idx, entry = self._nextEntry()

        gidx = ftGlyphSlot.index
        entry['glyphidx'] = gidx
        entry['typeface'] = self
        entry['hidx'] = hash((id(self), gidx))
        entry['lineSize'][:] = self.lineSize
        entry['ascenders'][:] = self.ascenders

        if gidx or not char.isspace():
            entry['advance'][:] = (1,-1)*ftGlyphSlot.padvance
            pbox = ftGlyphSlot.pbox
            entry['quad'][:] = (pbox * self._boxToQuad).sum(1)
        else: 
            entry['advance'][:] = 0
            entry['quad'][:] = 0

        entry['offset'][:] = 0
        entry['color'][:] = 0
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
        if not gi:
            if not sort['advance'].sum():
                return None

        ftGlyphSlot = ftFace.loadGlyph(gi)
        ftGlyphSlot.render()
        return ftGlyphSlot.getBitmapArray()

