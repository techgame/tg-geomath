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

from TG.geomath.data.vector import Vector, DataHostObject
from TG.geomath.data.box import Box

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlock(DataHostObject):
    tbox = Box.property([0.0, 0.0], dtype='f')
    box = Box.property([0.0, 0.0], dtype='f')

    def __init__(self, text, sorts, wrapSlice, typeset):
        self.text = text
        self.sorts = sorts
        self.wrapSlice = wrapSlice

        self.align = typeset.alignVector.copy()

        if text:
            self.init()

    def init(self):
        sorts = self.sorts

        maxIdx = sorts['lineSize'].argmax(0)[0]
        #self.maxIdx = maxIdx

        maxSort = sorts[maxIdx]
        lineSize = maxSort['lineSize']
        ascender, descender = maxSort['ascenders']

        # calculate the text-layout box
        off = sorts['offset']
        adv = sorts['advance']
        width = off[-1]-off[0] + adv[-1]

        sorts['quad'] -= off[0]

        advAxis = (lineSize <= 0)
        advAxis = advAxis * (advAxis.any() and 1 or 0)
        ascAxis = 1 - advAxis

        align = advAxis*self.align
        self.tbox.p0 = ascAxis*descender #- (align)*width
        self.tbox.p1 = ascAxis*ascender + width #+ (1-align)*width
        self.minSize = self.tbox.size
        self.box = self.tbox.copy()

    def layoutInBox(self, box):
        align = self.align
        self.box.at[align] = box.at[align]

