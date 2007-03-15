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

from itertools import izip

import numpy
from numpy import zeros_like, zeros, empty_like, empty, ndindex

from .layoutData import Rect, Vector
from .basicLayout import BaseLayoutStrategy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GridLayoutStrategy(BaseLayoutStrategy):
    nRows = nCols = None

    _haxis = numpy.array([1,0], 'b')
    _vaxis = numpy.array([0,1], 'b')

    def __init__(self, nRows=2, nCols=2):
        self.setRowCol(nRows=2, nCols=2)

    def getRowCol(self):
        return self.nRows, self.nCols
    def setRowCol(self, nRows=2, nCols=2):
        self.nRows = nRows
        self.nCols = nCols
    rowCol = property(getRowCol, setRowCol)

    def layout(self, cells, box, isTrial=False):
        if not cells:
            return box.pos.copy(), 0*box.size

        box = box.copy()

        # determin visible cells
        visCells = self.cellsVisible(cells)

        # figure out what our row and column sizes should be from the cells
        rowSizes, colSizes = self.rowColSizesFor(visCells, box, isTrial)

        if not isTrial:
            iCells = iter(visCells)
            iCellBoxes = self.iterCellBoxes(visCells, box, rowSizes, colSizes, isTrial)

            # let cells lay themselves out in their boxes
            for cbox, c in izip(iCellBoxes, iCells):
                c.layoutInBox(cbox)

            # hide cells that have no box
            for c in iCells:
                c.layoutHide()

        return self.layoutBox(visCells, box, rowSizes, colSizes, isTrial)
        
    def layoutBox(self, visCells, box, rowSizes, colSizes, isTrial=False):
        nRows = self.nRows; nCols = self.nCols

        lbox = box.copy()
        lsize = lbox.size

        # row and col sizes
        lsize = rowSizes.sum(0) + colSizes.sum(0)
        # plus borders along axis
        lsize += 2*self.outside + (nCols-1, nRows-1)*self.inside
        return lbox

    def iterCellBoxes(self, cells, box, rowSizes, colSizes, isTrial=False):
        posStart = box.pos + box.size*self._vaxis
        # come right and down by the outside border
        posStart += self.outside*(1,-1) 
        advCol = self._haxis*self.inside
        advRow = self._vaxis*self.inside

        cellBox = Rect()
        cellBox = box.fromSize((0,0))
        posRow = posStart
        posCol = cellBox.pos
        for row in rowSizes:
            # adv down by row
            posRow -= row

            posCol[:] = posRow
            for col in colSizes:
                # yield cell box
                cellBox.size[:] = row + col
                yield cellBox

                # adv right by col + inside border
                posCol += col + advCol

            # adv down by inside border
            posRow -= advRow

    def rowColSizesFor(self, cells, box, isTrial=False):
        vaxis = self._vaxis; haxis = self._haxis
        nRows = self.nRows; nCols = self.nCols

        cellsMinSize = self.cellsStats(cells)
        cellsMinSize *= (nCols, nRows)

        # figure out how much room the borders take
        borders = 2*self.outside + (nCols-1, nRows-1)*self.inside

        gridMinSize = borders + cellsMinSize
        box.size[:] = numpy.max([box.size, gridMinSize], 0)

        # figure out what our starting size minus borders is
        availSize = box.size - borders 
        cellSize = (availSize / (nCols, nRows))

        # repeat rowSize nRows times
        rowSizes = empty((nRows, 2), 'f')
        rowSizes[:] = (cellSize*vaxis)
        # repeat colSize nCols times
        colSizes = empty((nCols, 2), 'f')
        colSizes[:] = (cellSize*haxis)
        return rowSizes, colSizes

    def cellsStats(self, cells, default=zeros((2,), 'f')):
        cellsMinSize = numpy.min([(getattr(c, 'minSize', None) or default) for c in cells], 0)
        return cellsMinSize

