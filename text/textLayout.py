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

from itertools import izip, count
from numpy import vstack

from ..data import Rect, Vector

from . import textWrapping

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Text Layout
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextLayout(object):
    box = Rect.property()
    align = Vector.property([0, 1], '2f')
    crop = False
    gridCellAlign = True

    textData = None
    lineSpacing = 1
    lineOffset = 0

    _wrapMode = 'line'
    _wrapAlg = textWrapping.wrapModeMap[_wrapMode]
    def getWrapMode(self):
        return self._wrapMode
    def setWrapMode(self, wrapMode):
        self._wrapAlg = textWrapping.wrapModeMap[wrapMode]
        self._wrapMode = wrapMode
    wrapMode = property(getWrapMode, setWrapMode)

    def layoutMeshInBox(self, lbox):
        textData = self.textData
        lineAdvance = self.lineSpacing * textData.lineAdvance

        textOffsets = textData.getOffset()

        # get the line wrap slices
        iterWrapSlices = self._wrapAlg.iterWrapSlices(lbox.size, textData.text, textOffsets)

        # figure out line count, and setup wrap slice iterator
        if self.crop:
            nLinesCrop = lbox.size[1] // lineAdvance[1]
            iterLineCount = xrange(int(nLinesCrop))
        else: iterLineCount = count()
        lineSlices = zip(iterLineCount, iterWrapSlices)

        # starting position is top and size offset
        linePos = lbox.pos + lbox.size*self.align
        # offset by lineAdvance*count
        linePos -= self.lineOffset*lineAdvance

        # define some methods to handle alignment and offset
        halignVec = (1,0)*vstack([1-self.align, self.align])
        if self.gridCellAlign:
            def lineOffsetFor(lineSpan):
                aoff = (halignVec*lineSpan).sum(0)
                aoff -= linePos
                return aoff.round()
        else:
            def lineOffsetFor(lineSpan):
                aoff = (halignVec*lineSpan).sum(0)
                aoff -= linePos
                return aoff

        # grab the geometry we are laying out
        offset = textOffsets[...,:2]
        geometry = textData.geometry.copy()
        geomVec = geometry.v[...,:2]

        linesP0P1 = []
        for nline, ts in lineSlices:
            linePos -= lineAdvance
            # get the offset for textSlice
            toff = offset[ts.start:ts.stop+1]
            # align the line horizontally
            lineSpan = toff[[0, -1]].squeeze()
            lineOff = lineOffsetFor(lineSpan)
            linesP0P1.append(lineSpan - lineOff)
            # offset the geometry
            geomVec[ts] += toff[:-1] - lineOff

        # calculate our (line-oriented) bounding box
        if linesP0P1:
            linesP0P1 = vstack(linesP0P1)
            self.box.setCorners(linesP0P1.min(0), linesP0P1.max(0)+lineAdvance)
            geometry = geometry[:ts.stop]
        else: 
            self.box.setPosSize(linePos, lbox.size*(1,0))
            geometry = geometry[:0]

        #self.mesh = geometry
        return geometry

