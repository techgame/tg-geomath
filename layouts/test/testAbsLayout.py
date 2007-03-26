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

import unittest

from TG.geomath.layouts.cells import CellBox, Cell
from TG.geomath.layouts.absLayout import AbsLayoutStrategy

from TG.geomath.layouts.test.strategy import StrategyTestMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestAbsLayout(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = AbsLayoutStrategy
    hostBox = CellBox((0,0), (1000, 800))
    cells = [
        Cell(0, 200),
        Cell(1, 300),
        Cell(1, 200),
        ]

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[1000,800]])

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[50,50], [950, 750]])
        self.assertEqual(self.cbox[1], [[50,50], [950, 750]])
        self.assertEqual(self.cbox[2], [[50,50], [950, 750]])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

