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

from TG.geomath.layouts.flexGrid import FlexGridLayoutStrategy

from TG.geomath.layouts.test.strategy import Cell, Box
from TG.geomath.layouts.test.strategy import StrategyTestMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestFlexGridLayout(StrategyTestMixin, unittest.TestCase):
    StrategyFactory = lambda self: FlexGridLayoutStrategy((self.nRows, self.nCols))
    hostBox = Box((0,0), (1000, 800))
    nRows = 4; nCols = 4

    cells = [
        Cell(0, 100), Cell(0, 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell(0, 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell(0, 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell(0, 100), Cell(0, 100), Cell(0, 100),
        ]

    def testRowsCols(self):
        self.assertEqual(self.lstrat.nRows, self.nRows)
        self.assertEqual(self.lstrat.nCols, self.nCols)

    def testLBox(self):
        self.assertEqual(self.lbox, [[0,0],[1000,800]])

    def testCellBoxes(self):
        testData = [
            [[ 50, 582], [267, 750]], 
            [[277, 582], [495, 750]], 
            [[505, 582], [722, 750]], 
            [[732, 582], [950, 750]], 
            [[ 50, 405], [267, 572]], 
            [[277, 405], [495, 572]], 
            [[505, 405], [722, 572]], 
            [[732, 405], [950, 572]], 
            [[ 50, 227], [267, 395]], 
            [[277, 227], [495, 395]], 
            [[505, 227], [722, 395]], 
            [[732, 227], [950, 395]], 
            [[ 50,  50], [267, 217]], 
            [[277,  50], [495, 217]], 
            [[505,  50], [722, 217]], 
            [[732,  50], [950, 217]], 
        ]

        for i in xrange(len(testData)):
            self.assertEqual(self.cbox[i], testData[i])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestFlexGridLayoutDynamic(TestFlexGridLayout):
    cells = [
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        ]

    def testCellBoxes(self):
        testData = [
            [[ 50, 582], [150, 750]], 
            [[160, 582], [730, 750]], 
            [[740, 582], [840, 750]], 
            [[850, 582], [950, 750]], 
            [[ 50, 405], [150, 572]], 
            [[160, 405], [730, 572]], 
            [[740, 405], [840, 572]], 
            [[850, 405], [950, 572]], 
            [[ 50, 227], [150, 395]], 
            [[160, 227], [730, 395]], 
            [[740, 227], [840, 395]], 
            [[850, 227], [950, 395]], 
            [[ 50,  50], [150, 217]], 
            [[160,  50], [730, 217]], 
            [[740,  50], [840, 217]], 
            [[850,  50], [950, 217]], 
        ]
        
        for i in xrange(len(testData)):
            self.assertEqual(self.cbox[i], testData[i])


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestFlexGridLayoutDynamicHV(TestFlexGridLayout):
    cells = [
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        Cell((0,1), 100), Cell((1,1), 100), Cell((0,1), 100), Cell((0,1), 100),
        Cell(0, 100), Cell((1,0), 100), Cell(0, 100), Cell(0, 100),
        ]

    def testCellBoxes(self):
        testData = [
            [[ 50, 650], [150, 750]],
            [[160, 650], [730, 750]],
            [[740, 650], [840, 750]],
            [[850, 650], [950, 750]],
            [[ 50, 540], [150, 640]],
            [[160, 540], [730, 640]],
            [[740, 540], [840, 640]],
            [[850, 540], [950, 640]],
            [[ 50, 160], [150, 530]],
            [[160, 160], [730, 530]],
            [[740, 160], [840, 530]],
            [[850, 160], [950, 530]],
            [[ 50,  50], [150, 150]],
            [[160,  50], [730, 150]],
            [[740,  50], [840, 150]],
            [[850,  50], [950, 150]],
        ]
        
        for i in xrange(len(testData)):
            self.assertEqual(self.cbox[i], testData[i])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

