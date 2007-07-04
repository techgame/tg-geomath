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

from ..data import DataHostObject

from ..data.box import Box
from ..data.vector import Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LayoutCell(DataHostObject):
    """Abstract Base Class for a cell.

    Optional attributes:
        weight = Vector.property([0,0], 'f')
        minSize = Vector.property([0,0], 'f')
    """

    def layoutInBox(self, lbox):
        """Called with a Box instance or None when the cell has been placed"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

defaultBox = Box([0.,0.], dtype='f')

class BaseLayoutStrategy(DataHostObject):
    outside = Vector.property([0,0], 'f')
    inside = Vector.property([0,0], 'f')

    def layoutCalc(self, cells, box=defaultBox):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def layoutCells(self, cells, box=defaultBox):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def fit(self, cells, box=defaultBox):
        return self.layoutCalc(cells, box)
    def __call__(self, cells, box=defaultBox):
        return self.layoutCells(cells, box)

