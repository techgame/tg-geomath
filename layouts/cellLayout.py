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

from .layoutData import Vector, Rect

from .cells import BasicCell
from .absLayout import AbsLayoutStrategy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LayoutCell(BasicCell):
    layoutBox = Rect.property()
    strategy = AbsLayoutStrategy()

    def __init__(self, strategy=None, cells=None):
        if strategy is not None:
            self.strategy = strategy

        if cells is None:
            cells = []
        self.cells = cells

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    __call__ = property(lambda self: self.layoutInBox)
    layout = property(lambda self: self.layoutInBox)

    def layoutInBox(self, lbox=None):
        if lbox is None:
            lbox = self.box
        else: self.box.copyFrom(lbox)

        self.layoutBox = self.strategy(self.cells, lbox)
        self.onlayout(self, lbox)

    def layoutHide(self):
        self.onlayout(self, None)
        for c in self.cells:
            c.layoutHide()

