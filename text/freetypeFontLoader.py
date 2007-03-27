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

import itertools

from TG.freetype2.face import FreetypeFace

from ..data import blockMosaic
from . import font 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FreetypeFontLoader(object):
    LayoutAlgorithm = blockMosaic.BlockMosaicAlg
    FontFactory = font.Font

    def __init__(self, face, size=None, dpi=None, charset=NotImplemented):
        self.setFace(face)

        if size is not None:
            self.setSize(size, dpi)

        if charset is not NotImplemented:
            self.setCharset(charset)

    def __repr__(self):
        klass = self.__class__
        fmt = '<%s.%s %%s>' % (klass.__module__, klass.__name__,)
        info = '"%(familyName)s(%(styleName)s):%(lastSize)s"' % self.face.getInfo()
        return fmt % (info,)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _face = None
    def getFace(self):
        return self._face
    def setFace(self, face):
        if isinstance(face, basestring):
            if '#' in face:
                face, idx = face.rsplit('#', 1)
            else: idx = 0
            face = FreetypeFace(face, int(idx or 0))
        if face is not self._face:
            self._face = face
            del self.font
    face = property(getFace, setFace)

    def getSize(self):
        return self.face.getSize()
    def setSize(self, size, dpi=None):
        face = self.face
        if size is not None:
            face.setSize(size, dpi)
            del self.font
    size = property(getSize, setSize)

    _charset = None
    def getCharset(self):
        return self._charset
    def setCharset(self, charset):
        if charset == self._charset:
            return
        self._charset = charset
        del self.font
        
    charset = property(getCharset, setCharset)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _font = None
    def getFont(self):
        if self._font is None:
            self.setFont(self.compile())
        return self._font
    def setFont(self, font):
        self._font = font
    def delFont(self):
        self._font = None
    font = property(getFont, setFont, delFont)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Font compilation
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def compile(self, fontResult=None):
        face = self.getFace()
        charset = self.getCharset()

        if fontResult is None:
            fontResult = self.FontFactory()

        return self.compileFontOnto(fontResult, face, charset)

    @classmethod
    def compileFontOnto(klass, fontResult, face, charset):
        fontResult._onLoaderStart()
        count, gidxMap = klass._compileCharMap(fontResult, face, charset)

        # create a mosaicImage for the font mosaic, and run the mosaic algorithm
        mosaicImage, mosaic = klass._compileMosaicImage(fontResult, face, gidxMap)
        klass._compileGlyphData(fontResult, face, count, gidxMap, mosaicImage, mosaic)
        kernMap = klass._compileKerningMap(fontResult, face, gidxMap)

        fontResult._onLoaderFinish()
        return fontResult

    @classmethod
    def _compileCharMap(klass, fontResult, face, charset):
        charMap = {'\0': 0, '\n': 0, '\r': 0}
        gidxMap = {}
        aidxCounter = itertools.count(1)
        for char, gidx in face.iterCharIndexes(charset, True):
            aidx = aidxCounter.next()
            charMap.setdefault(char, aidx)
            gidxMap.setdefault(gidx, aidx)
        count = aidxCounter.next()

        fontResult.charMap = charMap
        return count, gidxMap

    @classmethod
    def _compileKerningMap(klass, fontResult, face, gidxMap):
        if not face.hasFlag('kerning'):
            return

        pointSize = fontResult.pointSize
        kerningMap = {}
        gi = gidxMap.items()
        getKerningByIndex = face.getKerningByIndex
        for l, li in gi:
            for r, ri in gi:
                k = getKerningByIndex(l, r)
                if k[0] or k[1]:
                    k = pointSize * [k[0], k[1], 0.]
                    kerningMap[(li,ri)] = k

        fontResult.kerningMap = kerningMap

    @classmethod
    def _compileMosaicImage(klass, fontResult, face, gidxMap):
        mosaicImage = fontResult.FontMosaicImage()
        if mosaicImage is None:
            return (None, {})

        mosaic, mosaicSize = klass._compileGlyphMosaic(fontResult, face, gidxMap, mosaicImage.getMaxMosaicSize())
        mosaicImage.createMosaic(mosaicSize)
        return (mosaicImage, mosaic)

    @classmethod
    def _compileGlyphMosaic(klass, fontResult, face, gidxMap, maxSize):
        if maxSize < 256: raise Exception("Max layout texture size is too small: %s" % (maxSize,))
        alg = klass.LayoutAlgorithm((maxSize-2, maxSize-2))

        mosaic = {}
        for gidx in gidxMap.iterkeys():
            glyph = face.loadGlyph(gidx)
            glyph.render()
            size = glyph.bitmapSize
            mosaic[gidx] = alg.addBlock(size)

        mosaicSize, layout, unplaced = alg.layout()

        if unplaced:
            raise Exception("Not all characters could be placed in mosaic.  (%s placed, %s unplaced)" % (len(layout), len(unplaced)))

        return mosaic, mosaicSize

    @classmethod
    def _compileGlyphData(klass, fontResult, face, count, gidxMap, mosaicImage, mosaic):
        # create the result arrays
        geometry = fontResult.FontGeometryArray.fromShape((count, 4, -1))
        advance = fontResult.FontAdvanceArray.fromShape((count, 1, -1))

        # cache some methods
        loadGlyph = face.loadGlyph
        verticesFrom = klass._verticesFrom
        advanceFrom = klass._advanceFrom

        if mosaicImage is not None:
            mosaicImage.select()
            renderGlyph = mosaicImage.renderGlyph

        # cache some variables
        pointSize = fontResult.pointSize

        # entry 0 is zero widht and has null geometry
        geometry.t[0] = 0
        geometry.v[0] = 0
        advance[0] = 0

        # record the geometry and advance for each glyph, and render to the mosaic
        for gidx, aidx in gidxMap.iteritems():
            glyph = loadGlyph(gidx)

            geoEntry = geometry[aidx]
            geoEntry.v = verticesFrom(glyph.metrics) * pointSize
            advance[aidx] = advanceFrom(glyph.advance) * pointSize

            block = mosaic.get(gidx)
            if block is None: 
                geoEntry.t = 0.0
            else: 
                geoEntry.t = renderGlyph(glyph, block.pos, block.size)

        fontResult.mosaicImage = mosaicImage
        fontResult.geometry = geometry
        fontResult.advance = advance
        fontResult.lineAdvance = (fontResult.pointSize[:2] * [0., face.lineHeight])

    @classmethod
    def _verticesFrom(klass, metrics):
        x0 = (metrics.horiBearingX)
        y0 = (metrics.horiBearingY - metrics.height - 1)

        x1 = (metrics.horiBearingX + metrics.width + 1)
        y1 = (metrics.horiBearingY)

        return [(x0, y0, 0.), (x1, y0, 0.), (x1, y1, 0.), (x0, y1, 0.)]

    @classmethod
    def _advanceFrom(klass, advance):
        return (advance[0], advance[1], 0.)

