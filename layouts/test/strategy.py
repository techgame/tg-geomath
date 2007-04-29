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

from TG.geomath.layouts.basic import LayoutCell, Box, Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestCell(LayoutCell):
    box = Box.property()
    weight = Vector.property([0,0], 'f')
    minSize = Vector.property([0,0], 'f')

    def __init__(self, weight=None, min=None):
        if weight is not None:
            self.weight = weight
        if min is not None:
            self.minSize = min

    def layoutInBox(self, lbox):
        if lbox is not None:
            self.box.pv = lbox.pv
        # else: hide

    @classmethod
    def new(klass):
        self = klass.__new__(klass)
        return self

    def copy(self):
        cpy = self.new()
        cpy.box = self.box.copy()
        cpy.weight = self.weight.copy()
        cpy.minSize = self.minSize.copy()
        return cpy

Cell = TestCell

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class StrategyTestMixin(object):
    StrategyFactory = None
    hostBox = None
    cells = []

    def setUp(self):
        hostBox = self.hostBox.copy()
        cells = [c.copy() for c in self.cells]

        lstrat = self.StrategyFactory() 
        self.lstrat = lstrat
        lstrat.inside = 10
        lstrat.outside = 50, 50

        lbox = lstrat.layoutCalc(cells, hostBox)
        self.lbox = lbox.astype(int).tolist()

        lstrat.layoutCells(cells, hostBox)
        self.cbox = [c.box.astype(int).tolist() for c in cells]

