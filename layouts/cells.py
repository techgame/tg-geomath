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
from .layoutData import CellBox, Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicCell(KVObject):
    box = CellBox.property()

    def layoutInBox(self, lbox):
        if lbox is not None:
            self.box.pv = lbox.pv
        # else: hide

    def copy(self):
        cpy = self.new()
        cpy.box = self.box.copy()
        return cpy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Cell(BasicCell):
    weight = Vector.property([0,0], 'f')
    minSize = Vector.property([0,0], 'f')

    def __init__(self, weight=None, min=None):
        BasicCell.__init__(self)
        if weight is not None:
            self.weight = weight
        if min is not None:
            self.minSize = min

    @classmethod
    def new(klass):
        self = klass.__new__(klass)
        return self

    def copy(self):
        cpy = BasicCell.copy(self)
        cpy.weight = self.weight.copy()
        cpy.minSize = self.minSize.copy()
        return cpy

