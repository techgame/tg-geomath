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

import numpy

from TG.geomath.layouts.grid import GridLayoutStrategy

from TG.geomath.layouts.test.strategy import Cell, Box
from TG.geomath.layouts.test.strategy import StrategyTestMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestGridLayout(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = lambda self: GridLayoutStrategy((self.nRows, self.nCols))
    hostBox = Box((0,0), (1000, 800))
    nRows = 2; nCols = 2

    @property
    def cells(self):
        return [Cell(0, (100, 200)) for ri, ci in numpy.ndindex((self.nRows, self.nCols))]

    def testRowsCols(self):
        self.assertEqual(self.lstrat.nRows, self.nRows)
        self.assertEqual(self.lstrat.nCols, self.nCols)

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[1000,800]])

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[ 50, 405], [495, 750]])
        self.assertEqual(self.cbox[1], [[505, 405], [950, 750]])
        self.assertEqual(self.cbox[2], [[ 50,  50], [495, 395]])
        self.assertEqual(self.cbox[3], [[505,  50], [950, 395]])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestGridLayout2x4(TestGridLayout):
    nRows = 2; nCols = 4

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[ 50, 405], [267, 750]])
        self.assertEqual(self.cbox[1], [[277, 405], [495, 750]])
        self.assertEqual(self.cbox[2], [[505, 405], [722, 750]])
        self.assertEqual(self.cbox[3], [[732, 405], [950, 750]])

        self.assertEqual(self.cbox[4], [[ 50,  50], [267, 395]])
        self.assertEqual(self.cbox[5], [[277,  50], [495, 395]])
        self.assertEqual(self.cbox[6], [[505,  50], [722, 395]])
        self.assertEqual(self.cbox[7], [[732,  50], [950, 395]])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestGridLayout3x3(TestGridLayout):
    nRows = 3; nCols = 3

    def testCellBoxes(self):
        self.assertEqual(self.cbox[0], [[ 50, 523], [343, 750]])
        self.assertEqual(self.cbox[1], [[353, 523], [646, 750]])
        self.assertEqual(self.cbox[2], [[656, 523], [950, 750]])

        self.assertEqual(self.cbox[3], [[ 50, 286], [343, 513]])
        self.assertEqual(self.cbox[4], [[353, 286], [646, 513]])
        self.assertEqual(self.cbox[5], [[656, 286], [950, 513]])

        self.assertEqual(self.cbox[6], [[ 50,  49], [343, 276]])
        self.assertEqual(self.cbox[7], [[353,  49], [646, 276]])
        self.assertEqual(self.cbox[8], [[656,  49], [950, 276]])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

