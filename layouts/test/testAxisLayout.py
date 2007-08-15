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

from TG.geomath.layouts.axis import HorizontalLayoutStrategy, VerticalLayoutStrategy

from TG.geomath.layouts.test.strategy import Cell, Box
from TG.geomath.layouts.test.strategy import StrategyTestMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestHorizontalAxisLayout(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = HorizontalLayoutStrategy
    hostBox = Box((0,0), (1000, 800))
    cells = [
        Cell(0, 200),
        Cell(1, 300),
        Cell(1, 200),
        ]

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[1000,800]])

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[ 50,50], [250, 750]])
        self.assertEqual(self.cbox[1], [[260,50], [650, 750]])
        self.assertEqual(self.cbox[2], [[660,50], [950, 750]])

class TestHorizontalAxisLayoutExceed(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = HorizontalLayoutStrategy
    hostBox = Box((0,0), (800, 800))
    cells = [
        Cell(0, 200),
        Cell(1, 300),
        Cell(1, 200),
        ]

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[820,800]])

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[ 50,50], [250, 750]])
        self.assertEqual(self.cbox[1], [[260,50], [560, 750]])
        self.assertEqual(self.cbox[2], [[570,50], [770, 750]])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestVerticalAxisLayout(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = VerticalLayoutStrategy
    hostBox = Box((0,0), (1000, 1000))
    cells = [
        Cell(0, 200),
        Cell(1, 300),
        Cell(1, 200),
        ]

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[1000,1000]])

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[50,750], [950, 950]])
        self.assertEqual(self.cbox[1], [[50,350], [950, 740]])
        self.assertEqual(self.cbox[2], [[50, 50], [950, 340]])

class TestVerticalAxisLayoutExceed(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = VerticalLayoutStrategy
    hostBox = Box((0,0), (1000, 800))
    cells = [
        Cell(0, 200),
        Cell(1, 300),
        Cell(1, 200),
        ]

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[1000,820]])

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[50,550], [950, 750]])
        self.assertEqual(self.cbox[1], [[50,240], [950, 540]])
        self.assertEqual(self.cbox[2], [[50, 30], [950, 230]])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

