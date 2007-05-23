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
from numpy import ndarray, float32, asarray, empty

from TG.freetype2.face import FreetypeFace
from TG.geomath.alg import blockMosaic

from . import font 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FreetypeLoader(object):
    pointSize = numpy.array([1./64., 1./64.])
    FaceObject = font.FaceObject

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Face compilation
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def compile(self, ftFace, result=None):
        if result is None:
            result = self.FaceObject()

        result._onLoaderStart()

        gidxMap = self.compileCharMap(result, ftFace)
        self.compileMetrics(result, ftFace, gidxMap)
        self.compileKerningMap(result, ftFace, gidxMap)

        result._onLoaderFinish()
        return result

    def compileCharMap(self, result, ftFace):
        charMap = {'\0': 0, '\n': 0, '\r': 0}
        gidxMap = [0]
        for char, gidx in ftFace.iterAllChars(True):
            charMap.setdefault(char, len(gidxMap))
            gidxMap.append(gidx)

        result.charMap = charMap
        return gidxMap

    def compileKerningMap(self, result, ftFace, gidxMap):
        if ftFace.hasFlag('kerning'):
            pointSize = self.pointSize
            getKerningByIndex = ftFace.getKerningByIndex

            kerningMap = {None: pointSize*0}
            for lidx, l in enumerate(gidxMap):
                for ridx, r in gidxMap:
                    k = pointSize * getKerningByIndex(l, r)
                    if k.any():
                        kerningMap[(li,ri)] = k
        else:
            kerningMap = None

        result.kerningMap = kerningMap

    def compileMetrics(self, result, ftFace, gidxMap):
        # create the result arrays
        count = len(gidxMap)
        verticies = empty((count, 4, 2), float32)
        advance = empty((count, 1, 2), float32)
        bitmapSize = empty((count, 1, 2), 'H')

        # cache some methods
        loadGlyph = ftFace.loadGlyph
        verticesFrom = self._verticesFrom
        advanceFrom = self._advanceFrom

        # cache some variables
        pointSize = self.pointSize

        # entry 0 is zero widht and has null geometry
        verticies[0] = 0
        advance[0] = 0

        # record the geometry and advance for each glyph
        for aidx, gidx in enumerate(gidxMap):
            glyph = loadGlyph(gidx)
            verticies[aidx] = verticesFrom(glyph.metrics) * pointSize
            advance[aidx] = advanceFrom(glyph.advance) * pointSize
            bitmapSize[aidx] = glyph.bitmapSize

        result.verticies = verticies
        result.advance = advance
        result.bitmapSize = bitmapSize
        result.lineAdvance = (0.,ftFace.lineHeight)*pointSize

    def _verticesFrom(self, metrics):
        x0 = (metrics.horiBearingX)
        y0 = (metrics.horiBearingY - metrics.height)

        x1 = (metrics.horiBearingX + metrics.width + 1)
        y1 = (metrics.horiBearingY + 1)

        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def _advanceFrom(self, advance):
        return list(advance)

