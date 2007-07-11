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

import weakref
import numpy

from TG.metaObserving import OBFactoryMap
from TG.geomath.data.vector import Vector, DataHostObject
from TG.geomath.data.box import Box
from TG.geomath.data.color import Color

from TG.geomath.layouts import AxisLayoutStrategy

from .mosaic import MosaicPageArena

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([0,1], 'b')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlockLine(DataHostObject):
    tbox = Box.property([0.0, 0.0], dtype='f')
    box = Box.property([0.0, 0.0], dtype='f')

    def __init__(self, block, slice, text, sorts, align):
        self.block = block
        self.align = align
        self.slice = slice
        self.text = text 
        self.init(sorts)

    def init(self, sorts):
        maxIdx = sorts['lineSize'].argmax(0)[0]

        maxSort = sorts[maxIdx]
        lineSize = maxSort['lineSize']
        ascender, descender = maxSort['ascenders']

        off = sorts['offset']
        adv = sorts['advance']
        width = off[-1]-off[0] + adv[-1]
        self._linearOffsetStart = off[0]

        advAxis = (lineSize <= 0)
        advAxis = advAxis * (advAxis.any() and 1 or 0)
        dscAxis = 1 - advAxis

        self.tbox.p0 = dscAxis*descender
        self.tbox.p1 = dscAxis*ascender + width

        size = self.tbox.size
        self.box.p0 = 0
        self.box.p1 = size
        self.minSize = size

    def getOffset(self):
        return self.box.p0 - self.tbox.p0 - self._linearOffsetStart
    offset = property(getOffset)

    def layoutInBox(self, box):
        align = self.align
        self.box.at[align] = box.at[align]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlock(DataHostObject):
    _fm_ = OBFactoryMap(
            PageArena = MosaicPageArena,
            Layout = TextLayoutStrategy,
            BlockLine = TextBlockLine,
            )
    box = Box.property([0.0, 0.0], dtype='f')
    fit = False
    arena = None
    lines = None

    def __init__(self, fit=False, clip=True, pageSize=None):
        self.init(fit, clip)
        self.createArena(pageSize)

    def init(self, fit, clip):
        self.clear()
        self.fit = fit
        self.clip = clip
        self.layoutAlg = self._fm_.Layout()

    @classmethod
    def createArena(klass, pageSize=None):
        if klass.arena is None:
            klass.arena = klass._fm_.PageArena(pageSize)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        self.lines = []
        self.meshes = {}
        self._mapIdxPush = []
        self._sorts = None

    def update(self, typeset):
        text, sorts, sectionList = typeset.compile()

        self.lines = []
        add = self.lines.append
        BlockLine = self._fm_.BlockLine
        for section in sectionList:
            for ws in section.wrap(text, sorts):
                if text[ws]:
                    add(BlockLine(self, ws, text[ws], sorts[ws], section.align))

        if sorts is not self._sorts:
            self._sorts = sorts
            self._arenaMapSorts(sorts)

        self.layout()
        return self

    _layoutDirty = False
    def layout(self, fit=None):
        if not self.lines:
            return

        if fit is None:
            fit = self.fit
        if fit:
            self.box[:] = self.layoutAlg.fit(self.lines, self.box)

        self.layoutAlg(self.lines, self.box)
        self._layoutDirty = True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getSourceColor(self):
        return self._sorts['color']
    srcColor = sourceColor = property(getSourceColor)

    def getColor(self):
        return self.meshes['color']
    def setColor(self, value):
        self.meshes['color'][:] = value
    color = property(getColor, setColor)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _sorts = None
    def _arenaMapSorts(self, sorts):
        pageMap, texCoords = self.arena.texCoords(sorts)
        self.pageMap = pageMap

        self._mask = numpy.ones(len(sorts), 'B')

        color = Color.fromShape((len(sorts), 4, 4), 'B')
        color[:] = sorts['color']

        meshes = dict(
            vertex = sorts['quad'].copy(),
            texCoords = texCoords,
            color = color,
            pageIdxMap = {},)

        self.meshes = meshes
        self._updatePageIdxMap(False)

    def _updatePageIdxMap(self, useMask=True):
        addOuter = numpy.add.outer
        ar4 = numpy.arange(4, dtype='H')

        pageIdxMap = self.meshes['pageIdxMap']
        if useMask:
            mask = self._mask
            for page, pim in self.pageMap.iteritems():
                if page is not None:
                    mpim = pim.compress(mask[pim])
                    entry = pageIdxMap[page]
                    entry[:len(mpim)] = addOuter(4*mpim, ar4)
                    entry[len(mpim):] = 0
        else:
            for page, pim in self.pageMap.iteritems():
                if page is not None:
                    pageIdxMap[page] = addOuter(4*pim, ar4)

        return pageIdxMap

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def apply(self):
        if not self._layoutDirty:
            return False

        self._applyLayout()
        if self.clip:
            self._clipLines()
        return True

    def _applyLayout(self):
        meshes = self.meshes
        sorts = self._sorts
        vertex = meshes['vertex']

        for line in self.lines:
            sl = line.slice
            sl_sorts = sorts[sl]
            vertex[sl] = sl_sorts['quad']
            vertex[sl] += sl_sorts['offset']
            vertex[sl] += line.offset

    def _clipLines(self):
        boxYv = self.box.yv
        for line in self.lines:
            sl = line.slice
            v = (-1,1)*(boxYv - line.box.yv)
            self._mask[sl] = (v >= 0).all()

        self._updatePageIdxMap(True)
        return True

