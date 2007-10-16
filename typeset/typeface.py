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

import string 

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
    def setSorts(self, key, value, idx=None):
        if idx is None:
            idx = slice(None, self._arrPool.idx)
        self._arrPool.pool[idx][key] = value
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

    isKerned = False
    lineSize = None
    ascenders = None

    dpiScale = 1

    def __init__(self, ftFace, size=None, dpi=2*72, dpiLayout=72):
        if isinstance(ftFace, basestring):
            ftFace = FreetypeFace(ftFace)

        if size is not None:
            ftFace.setCharSize(size, dpi)
            if dpiLayout:
                self.dpiScale = float(dpiLayout)/dpi

        self._ftFace = ftFace
        self._createPool(ftFace.numGlyphs)

        lh = self.dpiScale * ftFace.lineHeight / 64
        if ftFace.isLayoutVertical():
            self.lineSize = numpy.array([lh,0], 'f')
        else: 
            self.lineSize = numpy.array([0,lh], 'f')

        self.ascenders = numpy.array([
                [self.dpiScale * ftFace.lineAscender / 64], 
                [self.dpiScale * ftFace.lineDescender / 64]], 'f')

        self.isKerned = ftFace.hasFlag('kerning')
        self._initFace()

    def _initFace(self):
        pass

    def kern(self, sorts, advance=None):
        if not self.isKerned:
            return advance

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

        adv, quad = self._geomForGlyph(gidx, ftGlyphSlot, char)
        entry['advance'][:] = adv
        entry['quad'][:] = quad
        entry['offset'][:] = 0
        entry['color'][:] = 0
        return idx

    def _geomForGlyph(self, gidx, ftGlyphSlot, char):
        if gidx:
            adv = (1,-1) * ftGlyphSlot.padvance * self.dpiScale

            pbox = ftGlyphSlot.pbox
            quad = (pbox * self.dpiScale * self._boxToQuad).sum(1)
            return adv, quad
        else: return 0, 0

    def loadAll(self):
        ftFace = self._ftFace
        for cc, gi in ftFace.iterAllChars(True):
            ftGlyphSlot = ftFace.loadGlyph(gi)
            idx = self._loadGlyph(ftGlyphSlot)
            self[ord(cc)] = idx

    def bitmapFor(self, sort):
        ftFace = self._ftFace
        gi = int(sort['glyphidx'])
        if gi or sort['advance'].sum():
            ftGlyphSlot = ftFace.loadGlyph(gi)
            return ftGlyphSlot.render()


class FTFixedTypeface(FTTypeface):
    fixedAdv = None
    _fixedWidthChars = string.letters

    def _geomForGlyph(self, gidx, ftGlyphSlot, char):
        if gidx:
            adv = self.fixedAdv
            if adv is None:
                adv = dpiScale*(1,-1)*ftGlyphSlot.padvance

            pbox = ftGlyphSlot.pbox
            quad = (self.dpiScale * pbox * self._boxToQuad).sum(1)
            return adv, quad
        else: return 0, 0

    def _initFace(self):
        wsort = self.translate(self._fixedWidthChars)

        # find the fixedAdv for this font
        self.fixedAdv = wsort['advance'].max(0)

        # update already populated sorts
        self.setSorts('advance', self.fixedAdv)

