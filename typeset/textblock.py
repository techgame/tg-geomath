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
    dirty = True

    def __init__(self, block, slice, text, sorts, align):
        self.block = block
        self.align = align
        self.slice = slice
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
        self.dirty = True

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

    def __init__(self, fit=False, pageSize=None):
        self.init(fit)
        self.createArena(pageSize)

    def init(self, fit=True):
        self.clear()
        self.fit = fit
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

        self._arenaMapSorts(sorts)

        self.layout()
        return self

    def layout(self, fit=None):
        if not self.lines:
            return

        if fit is None:
            fit = self.fit
        if fit:
            self.box[:] = self.layoutAlg.fit(self.lines, self.box)
        self.layoutAlg(self.lines, self.box)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getAtColor(self):
        return AtColorSyntax(self)
    def setAtColor(self, value):
        self.color[:] = value
    color = property(getAtColor, setAtColor)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _sorts = None
    def _arenaMapSorts(self, sorts):
        if sorts is self._sorts:
            return 
        self._sorts = sorts

        pageMap, mapIdxPush, mapIdxPull, texCoords = self.arena.texMap(sorts)
        self._mapIdxPush = mapIdxPush

        count = len(mapIdxPull)
        meshes = dict(
            vertex = numpy.zeros((count, 4, 2), 'l'),
            color = Color.fromShape((count, 4, 4), 'B'),
            texture = numpy.zeros((count, 4, 2), 'f'),
            pageMap = pageMap,
            )
        self.meshes = meshes

        mapped_sorts = sorts[mapIdxPull]
        meshes['quads'] = mapped_sorts['quad']
        meshes['color'][:] = mapped_sorts['color']
        if len(texCoords):
            meshes['texture'][:] = texCoords[mapIdxPull]

    def apply(self):
        self.applyLayout()

    def applyLayout(self):
        for line in self.lines:
            if not line.dirty:
                break

            idxPush = self._mapIdxPush[line.slice]

            meshes = self.meshes
            vertex = meshes['vertex']
            vertex[idxPush] = meshes['quads'][idxPush] 
            vertex[idxPush] += self._sorts['offset'][line.slice]
            vertex[idxPush] += line.offset

            line.dirty = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AtColorSyntax(object):
    def __init__(self, textBlock):
        self.textBlock = textBlock

    def __repr__(self):
        return repr(self[:])

    def getName(self): return self[:].name
    def setName(self, name): 
        self[:].name = name
    name = property(getName, setName)

    def getHex(self): return self[:].hex
    def setHex(self, hex): 
        self[:].hex = hex
    hex = property(getHex, setHex)

    def __len__(self):
        return len(self.textBlock._mapIdxPush)

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

