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

from TG.kvObserving import KVObject
from .layoutData import Box, Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicCell(KVObject):
    box = Box.property()

    def layoutInBox(self, lbox):
        if lbox is not None:
            self.box.pv = lbox.pv
        # else: hide

    # Note: You can provide layoutAdjustSize() if you want to adjust the size
    # alloted to your cell.  If not present, some algorithms run faster
    ##def layoutAdjustSize(self, lsize):
    ##    # lsize parameter must not be modified... use copies!
    ##    return lsize

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Cell(BasicCell):
    weight = Vector.property([0,0], 'f')
    minSize = Vector.property([0,0], 'f')

    def __init__(self, weight=None, min=None):
        BasicCell.__init__(self)
        if weight is not None:
            self.weight[:] = weight
        if min is not None:
            self.minSize[:] = min

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ MaxSize support
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def layoutAdjustForMaxSize(self, lsize):
    # lsize parameter must not be modified... use copies!
    maxSize = self.maxSize
    idx = (maxSize > 0) & (maxSize < lsize)
    if idx.any():
        lsize = lsize.copy()
        lsize[idx] = maxSize
    return lsize

class MaxSizeCell(Cell):
    maxSize = Vector.property([0,0], 'f')

    def __init__(self, weight=None, min=None, max=None):
        Cell.__init__(self, weight, min)
        if max is not None:
            self.maxSize[:] = max

    layoutAdjustSize = layoutAdjustForMaxSize

