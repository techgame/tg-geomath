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
from numpy import floor, ceil

from .layoutData import Rect, Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicCell(object):
    visible = True
    box = Rect.property()

    # Note: You can provide this function if you want to adjust the size
    # alloted to your cell.  If not present, some algorithms run faster
    ##def adjustSize(self, lsize):
    ##    # lsize parameter must not be modified... use copies!
    ##    return lsize

    def layoutInBox(self, lbox):
        cellBox = self.box

        # lbox.pos and lbox.size parameters must not modified... use copies!
        ceil(lbox.pos, cellBox.pos)
        floor(lbox.size, cellBox.size)

        self.onlayout(self, cellBox)

    def layoutHide(self):
        self.onlayout(self, None)

    def onlayout(self, cell, cbox):
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Cell(BasicCell):
    weight = Vector.property([0,0], '2f')
    minSize = Vector.property([0,0], '2f')

    def __init__(self, weight=None, min=None):
        BasicCell.__init__(self)
        if weight is not None:
            self.weight[:] = weight
        if min is not None:
            self.minSize[:] = min

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ MaxSize support
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def adjustForMaxSize(self, lsize):
    # lsize parameter must not be modified... use copies!
    maxSize = self.maxSize
    idx = (maxSize > 0) & (maxSize < lsize)
    if idx.any():
        lsize = lsize.copy()
        lsize[idx] = maxSize
    return lsize

class MaxSizeCell(Cell):
    maxSize = Vector.property([0,0], '2f')

    def __init__(self, weight=None, min=None, max=None):
        Cell.__init__(self, weight, min)
        if max is not None:
            self.maxSize[:] = max

    adjustSize = adjustForMaxSize

