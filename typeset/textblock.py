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
    scroll = Vector.property([0., 0.], 'f')

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
        self.maxSort = maxSort
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

    # adj_offset helps to correct for texel clipping due to glScale() introduced errors
    _adj_offset = numpy.array([
            [-0.15, -0.25],
            [+0.15, -0.25],
            [+0.15, +0.25],
            [-0.15, +0.25]], 'f')
    def getOffset(self, adj=True):
        off = (self.box.p0 - self.tbox.p0 - self._linearOffsetStart)
        if adj: 
            return off + self._adj_offset
        else: return off
    offset = property(getOffset)

    def layoutInBox(self, box):
        if box:
            align = self.align
            self.box.at[align] = box.at[align]

    def buildSelectionBoxes(self, sel, sorts, xfrm):
        s0 = max(sel.start, self.slice.start)
        s1 = min(sel.stop, self.slice.stop)
        if s1 > s0:
            subsel = slice(s0, s1)
            asc, dec = self.maxSort['ascenders']
            off0, off1 = sorts['offset'][[s0,s1]]
            p0 = [off0[0][0], dec[0]]
            p1 = [off1[0][0], asc[0]]
            b = Box(p0, p1)
            b += self.getOffset(False)
            return [b.geoXfrm(xfrm)]
        else: return []

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
    textBoxAlign = (0.0, 1.0)

    def __init__(self, fit=False, clip=False, pageSize=None):
        self.init(fit, clip)
        self.createArena(pageSize)

    def buildSelectionBoxes(self, sel, xfrm):
        sorts = self._sorts
        r = sum((l.buildSelectionBoxes(sel, sorts, xfrm) for l in self.lines), [])
        if r: r = numpy.concatenate(r)
        return r

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

    def __nonzero__(self):
        sorts = self._sorts
        if sorts is None: 
            return False
        return len(sorts) > 0

    def clear(self):
        self.lines = []
        self.meshes = {}
        self._mapIdxPush = []
        self._sorts = None
        self.invalidate()

    dirty = False
    def invalidate(self):
        self.dirty = True

    def update(self, typeset):
        text, sorts, sectionList = typeset.compile()

        self.text = text
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
        self.dirty = False
        return self

    _layoutDirty = False
    def layout(self, fit=None):
        if not self.lines:
            return

        if fit is None:
            fit = self.fit

        fitbox = self.layoutAlg.fit(self.lines, self.box, at=(0,1))
        self.fitbox = fitbox
        if fit:
            self.box.setSize(fitbox.size, at=(0,1))

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

    def getLeading(self):
        return self.layoutAlg.inside[1]
    def setLeading(self, leading):
        self.layoutAlg.inside[1] = leading
    leading = property(getLeading, setLeading)

    def getScroll(self):
        return self.layoutAlg.scroll
    def setScroll(self, scroll):
        self.layoutAlg.scroll = scroll
    scroll = property(getScroll, setScroll)

    def scrollToYPos(self, y):
        tH = self.textHeight; bH = self.box.height
        y = min(max(0, y), max(0, tH-bH))
        self.scroll[1] = y
        self.invalidate()
    def scrollPos(self, delta):
        self.scrollToYPos(self.scroll[1] + delta)

    def posForIdx(self, idx, dLines=0, incHeight=False):
        sidx = min(idx, len(self.text)-1)
        cs = self._sorts[sidx]
        V = self.meshes['vertex'][sidx]
        V = V[0] - cs['quad'][0]
        if dLines:
            V -= dLines * cs['lineSize']
        if incHeight:
            return V, cs['lineSize'][1]
        else: return V

    def makeIdxVisible(self, idx, margin=True, dLines=0):
        pos, lineHeight = self.posForIdx(idx, dLines, True)
        if margin is True: margin = lineHeight
        return self.makePosVisible(pos, margin)

    def makePosVisible(self, pos, margin=0):
        box = self.box
        if margin >= box.height:
            return False

        y = pos[1]
        dT = y+margin - box.top
        if dT <= 0:
            dT = y-margin - box.bottom
            if dT >= 0:
                return False

        self.scrollPos(-dT)
        return True

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

        textBoxAlign = self.textBoxAlign
        h,v = textBoxAlign
        alignOffset = (1,-1)*(self.box.at[h,v] - self.fitbox.at[h,v])

        for line in self.lines:
            sl = line.slice
            sl_sorts = sorts[sl]
            vertex[sl] = sl_sorts['quad']
            vertex[sl] += sl_sorts['offset']
            vertex[sl] += line.offset + alignOffset

    def _clipLines(self):
        boxYv = self.box.yv
        for line in self.lines:
            sl = line.slice
            v = (-1,1)*(boxYv - line.box.yv)
            self._mask[sl] = (v >= 0).all()

        self._updatePageIdxMap(True)
        return True

    @property
    def textHeight(self):
        return sum(line.tbox.height for line in self.lines)

