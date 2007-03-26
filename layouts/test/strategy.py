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

from TG.geomath.layouts.cells import CellBox, Cell

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
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

        lbox = lstrat.layout(cells, hostBox, True)
        self.lbox = lbox.astype(int).tolist()

        lstrat.layout(cells, hostBox, False)
        self.cbox = [c.box.astype(int).tolist() for c in cells]

