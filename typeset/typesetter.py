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
from numpy import zeros, empty, recarray

from TG.metaObserving import OBFactoryMap
from TG.geomath.data.color import Color, DataHostObject
from TG.geomath.data.vector import Vector, DataHostObject

from .typeface import dtype_sorts
from .wrap import wrapModeMap
from .textblock import TextBlock

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_alignmentReverse = {(0, 0.0): 'left', (1, 0.0): "bottom", (0, 0.5): 'center', (1, 0.5): 'center', (0, 1.0): 'right', (1, 1.0): 'top'}
_alignmentLookup = {'left':0.0, 'center':0.5, 'right':1.0, 'top':1.0, 'bottom':0.0}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TypesetSection(DataHostObject):
    _fm_ = OBFactoryMap(
            TextBlock = TextBlock,
            wrapModes = wrapModeMap,
            emptySorts = numpy.empty(0, dtype_sorts))

    align = Vector.property([0.0, 0.0])
    wrapSize = Vector.property([0,0])
    wrapMode = 'line'

    def __nonzero__(self):
        return self.end is not None

    start = None
    end = None
    def getTextRange(self):
        return slice(self.start, self.end or self.start)
    textRange = property(getTextRange)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getFormat(self):
        return dict(align=self.align.copy(), wrapMode=self.wrapMode, wrapSize=self.wrapSize.copy())
    format = property(getFormat)

    def attr(self, *args, **kw):
        if kw:
            args += (kw.items(),)
        for attrs in args:
            for n, v in attrs:
                setattr(self, n, v)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def wrap(self, text, sorts):
        wrapMode = self.wrapMode
        if not hasattr(wrapMode, 'wrapSlices'):
            if isinstance(wrapMode, basestring):
                wrapMode = wrapMode.lower()
            wrapMode = self._fm_.wrapModes[wrapMode]

        return wrapMode.wrapSlices(self.wrapSize, self.textRange, text, sorts['offset'])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TypeSetter(DataHostObject):
    _fm_ = OBFactoryMap(
            TextBlock = TextBlock,
            Section = TypesetSection,
            wrapModes = wrapModeMap,
            emptySorts = numpy.empty(0, dtype_sorts)
            )

    # glyph and spacing options
    face = None
    kern = False
    color = Color.property('#ff')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, **kw):
        self.clear()
        if kw: self.attr(kw.items())

    def attr(self, *args, **kw):
        if kw:
            args += (kw.items(),)
        for attrs in args:
            for n, v in attrs:
                setattr(self, n, v)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _block = None
    def getBlock(self):
        if self._block is None:
            self.setBlock(self._fm_.TextBlock())
        return self._block
    def setBlock(self, block):
        self._block = block
    block = property(getBlock, setBlock)

    def getBox(self): return self.block.box
    def setBox(self, box): self.block.box = box
    box = property(getBox, setBox)

    def getFit(self): return self.block.fit
    def setFit(self, fit): self.block.fit = fit
    fit = property(getFit, setFit)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def update(self):
        return self.block.update(self)

    def compile(self):
        return self.text, self.sorts, self.sectionList

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _sectionList = None
    def getSectionList(self):
        return self._sectionList
    def setSectionList(self, sectionList):
        self._sectionList = sectionList
    def delSectionList(self):
        if self._sectionList:
            format = self.section.format
        else: format = {}
        self._sectionList = []
        self.newSection(**format)
    sectionList = property(getSectionList, setSectionList, delSectionList)

    def getSection(self):
        return self.sectionList[-1]
    section = property(getSection)

    def newSection(self, *args, **kw):
        sectionList = self.sectionList
        if sectionList:
            section = sectionList[-1]
            if not section:
                # current section is "empty", return it
                section.attr(*args, **kw)
                return section

        else: section = None

        newSection = self._fm_.Section()
        newSection.start = len(self.text)

        if section is not None:
            newSection.attr(section.format.items())
        newSection.attr(*args, **kw)

        sectionList.append(newSection)
        return newSection

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ File-like write typesetting
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _typsetOffset = 0
    _rope = None
    text = u''

    def clear(self):
        self._typsetOffset = 0
        self._rope = []
        self.text = u''
        self._sorts = self._fm_.emptySorts

        self.delSectionList()

    softspace = False
    def write(self, text, **kw):
        if kw: self.attr(kw.items())

        if not text: return 
        if not isinstance(text, unicode):
            text = unicode(text)

        sorts = self.face.translate(text)
        sorts['color'] = self.color

        advance = sorts['advance']
        offset = sorts['offset']
        if self.kern:
            self.face.kern(sorts, advance)

        offset[0] += self._typsetOffset
        numpy.add(offset[:-1], advance[:-1], offset[1:])
        self._typsetOffset = offset[-1] + advance[-1]

        curText = self.text
        sl = slice(len(curText), len(curText)+len(text))
        self.text = curText + text
        self._rope.append(sorts)

        self.section.end = len(self.text)
        return sl

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _sorts = _fm_.emptySorts
    def getSorts(self):
        sorts = self._sorts
        rope = self._rope
        if len(rope):
            rope.insert(0, sorts)
            sorts = numpy.concatenate(rope)
            del rope[:]
            self._sorts = sorts
        return sorts
    sorts = property(getSorts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Typesetting Style
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getAlign(self, axis=0):
        aw = self.section.align[axis]
        return _alignmentReverse.get((axis, self._align), self._align)
    def setAlign(self, align, axis=0):
        aw = _alignmentLookup.get(align, None)
        if aw is None:
            aw = float(align)
        section = self.newSection()
        section.align[axis] = aw
    align = property(getAlign, setAlign)

    def getVerticalAlign(self):
        return self.getAlign(1)
    def setVerticalAlign(self, align):
        self.setAlign(align, 1)
    valign = verticalAlign = property(getVerticalAlign, setVerticalAlign)

    def getWrapMode(self):
        return self.section.wrapMode
    def setWrapMode(self, wrapMode):
        self.newSection(wrapMode=wrapMode)
    wrapMode = property(getWrapMode, setWrapMode)

    def getWrapSize(self):
        return self.section.wrapSize
    def setWrapSize(self, wrapSize, all=False):
        if all:
            for section in self.sectionList:
                section.wrapSize = wrapSize
        else:
            self.newSection(wrapSize=wrapSize)
    wrapSize = property(getWrapSize, setWrapSize)


