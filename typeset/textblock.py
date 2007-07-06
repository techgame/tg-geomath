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

from TG.geomath.data.vector import Vector, DataHostObject
from TG.geomath.data.box import Box
from TG.geomath.data.color import Color

from TG.geomath.layouts import AxisLayoutStrategy

from .mosaic import MosaicPageArena

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlock(DataHostObject):
    box = Box.property([0.0, 0.0], dtype='f')
    fit = True

    def __init__(self, fit=True, pageSize=None):
        self.createLayout(fit)
        self.createArena(pageSize)

    def createArena(self, pageSize=None):
        self.arena = MosaicPageArena(pageSize)

    def createLayout(self, fit=True):
        self.fit = fit
        self.layoutAlg = TextLayoutStrategy()

    def update(self, typeset, clear=True):
        self.align = typeset.alignVector.copy()

        text, sorts, wrapSlices = typeset.wrap()
        if clear:
            typeset.clear()
        
        self.text = text
        self._arenaMapSorts(sorts)

        wrSelf = weakref.proxy(self)
        self.lines = [TextBlockLine(wrSelf, ws, text[ws], sorts[ws]) for ws in wrapSlices]
        self.layout()

    def layout(self, fit=None):
        if fit is None:
            fit = self.fit

        if fit:
            self.box[:] = self.layoutAlg.fit(self.lines, self.box)
        self.layoutAlg(self.lines, self.box)

    def _arenaMapSorts(self, sorts):
        pageMap, mapIdxPush, mapIdxPull, texCoords = self.arena.texMap(sorts)
        self.texCoords = texCoords

        self.pageMap = pageMap
        self._mapIdxPush = mapIdxPush
        self._mapIdxPull = mapIdxPull

        count = len(mapIdxPull)
        meshes = dict(
            vertex = numpy.empty((count, 4, 2), 'l'),
            color = Color.fromShape((count, 4, 4), dtype='B'),
            texture = numpy.empty((count, 4, 2), 'f'),
            )
        self.meshes = meshes

        mapped_sorts = sorts[mapIdxPull]
        meshes['quads'] = mapped_sorts['quad']
        meshes['color'][:] = mapped_sorts['color']
        meshes['texture'][:] = texCoords[mapIdxPull]

    def updateVertex(self, lineSlice, lineOffsets):
        idxPush = self._mapIdxPush[lineSlice]

        meshes = self.meshes
        meshes['vertex'][idxPush] = meshes['quads'][idxPush] + lineOffsets

    def _getAtColor(self):
        return AtColorSyntax(self)
    def _setAtColor(self, value):
        self.color[:] = value
    color = property(_getAtColor, _setAtColor)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([0,1], 'b')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlockLine(DataHostObject):
    tbox = Box.property([0.0, 0.0], dtype='f')
    box = Box.property([0.0, 0.0], dtype='f')

    def __init__(self, host, slice, text, sorts):
        self.host = host
        self.align = host.align
        self.slice = slice
        self.text = text
        self.init(sorts)

    def init(self, sorts):
        maxIdx = sorts['lineSize'].argmax(0)[0]

        maxSort = sorts[maxIdx]
        lineSize = maxSort['lineSize']
        ascender, descender = maxSort['ascenders']

        off = sorts['offset']
        self.linearOffset = off
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
        delta = self.box.p0 - self.tbox.p0 - self._linearOffsetStart
        return self.linearOffset + delta
    offset = property(getOffset)

    def layoutInBox(self, box):
        align = self.align
        self.box.at[align] = box.at[align]
        self.host.updateVertex(self.slice, self.offset)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AtColorSyntax(object):
    def __init__(self, textBlock):
        self.textBlock = textBlock

    def __repr__(self):
        return repr(self[:])
    def getName(self): return self[:].name
    def setName(self, name): self[:].name = name
    name = property(getName, setName)

    def getHex(self): return self[:].hex
    def setHex(self, hex): self[:].hex = hex
    hex = property(getHex, setHex)

    def __getitem__(self, idx):
        textBlock = self.textBlock
        idxPush = textBlock._mapIdxPush[idx]
        color = textBlock.meshes['color']
        return color[idxPush]

    def __setitem__(self, idx, value):
        value = Color(value)
        value.shape = ((1,1,) + value.shape)[-3:]

        textBlock = self.textBlock
        idxPush = textBlock._mapIdxPush[idx]
        color = textBlock.meshes['color']
        color[idxPush] = value

