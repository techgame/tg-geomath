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

from TG.metaObserving import MetaObservableType

from ..data.box import Box
from ..data.vector import Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LayoutCell(object):
    """Abstract Base Class for a cell.

    Optional attributes:
        weight = Vector.property([0,0], 'f')
        minSize = Vector.property([0,0], 'f')
    """

    __metaclass__ = MetaObservableType

    def layoutInBox(self, lbox):
        """Called with a Box instance or None when the cell has been placed"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseLayoutStrategy(object):
    __metaclass__ = MetaObservableType

    outside = Vector.property([0,0], 'f')
    inside = Vector.property([0,0], 'f')

    def layoutCalc(self, cells, box):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def layoutCells(self, cells, box):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

