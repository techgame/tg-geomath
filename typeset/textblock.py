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
        self.block.updateVertex(self.slice, self.offset)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlockLineset(DataHostObject):
    _fm_ = OBFactoryMap(BlockLine = TextBlockLine)

    def __init__(self, textBlock):
        self._wrTextBlock = weakref.proxy(textBlock) 
        self.clear()

    def clear(self):
        self.slEnd = 0
        self.textRope = []
        self.sortsRope = []
        self.lines = []

    def flush(self, typeset):
        if not typeset.text:
            return 

        align = typeset.alignVector.copy()
        text, sorts, wrapSlices = typeset.wrap()
        typeset.clear()
        
        off = self.slEnd
        soff = lambda ws: slice(ws.start+off, ws.stop+off)

        blk = self._wrTextBlock
        BlockLine = self._fm_.BlockLine
        self.lines.extend(BlockLine(blk, soff(ws), text[ws], sorts[ws], align) for ws in wrapSlices if text[ws])

        self.slEnd = off + len(sorts)
        self.textRope.append(text)
        self.sortsRope.append(sorts)

    def compile(self, typeset=None):
        if typeset is not None:
            self.flush(typeset)

        text = ''.join(self.textRope)
        sorts = numpy.concatenate(self.sortsRope)
        lines = self.lines
        self.clear()

        return text, sorts, lines

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlock(DataHostObject):
    _fm_ = OBFactoryMap(
            Lineset = BlockLineset,
            PageArena = MosaicPageArena,
            Layout = TextLayoutStrategy,
            )
    box = Box.property([0.0, 0.0], dtype='f')
    fit = False
    arena = None

    def __init__(self, fit=False, pageSize=None):
        self.init(fit)
        self.createArena(pageSize)

    def init(self, fit=True):
        self.lineset = self._fm_.Lineset(self)

        self.fit = fit
        self.layoutAlg = self._fm_.Layout()

    @classmethod
    def createArena(klass, pageSize=None):
        if klass.arena is None:
            klass.arena = klass._fm_.PageArena(pageSize)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        self.lineset.clear()
        self.lines = []

        self.meshes = {}
        self._mapIdxPush = []

    def flush(self, typeset):
        self.lineset.flush(typeset)
        return self

    def compile(self, typeset=None):
        text, sorts, lines = self.lineset.compile(typeset)

        self.text = text
        self.lines = lines
        self._arenaMapSorts(sorts)
        self.layout()
        return self

    def layout(self, fit=None):
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

    def _arenaMapSorts(self, sorts):
        pageMap, mapIdxPush, mapIdxPull, texCoords = self.arena.texMap(sorts)
        self._mapIdxPush = mapIdxPush

        count = len(mapIdxPull)
        meshes = dict(
            vertex = numpy.empty((count, 4, 2), 'l'),
            color = Color.fromShape((count, 4, 4), 'B'),
            texture = numpy.empty((count, 4, 2), 'f'),
            pageMap = pageMap,
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

