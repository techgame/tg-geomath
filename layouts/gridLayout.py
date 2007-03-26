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

from .layoutData import CellBox, Vector
from .basicLayout import BaseLayoutStrategy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GridLayoutStrategy(BaseLayoutStrategy):
    nRows = nCols = None

    _haxis = Vector([1,0], 'b')
    _vaxis = Vector([0,1], 'b')

    def __init__(self, nRows=2, nCols=2):
        self.setRowCol(nRows, nCols)

    def getRowCol(self):
        return self.nRows, self.nCols
    def setRowCol(self, nRows=2, nCols=2):
        self.nRows = nRows
        self.nCols = nCols
    rowCol = property(getRowCol, setRowCol)

    def layout(self, cells, box, isTrial=False):
        rbox = box.copy()
        lbox = box.copy()

        # figure out what our row and column sizes should be from the cells
        rowSizes, colSizes = self.rowColSizesFor(cells, lbox)

        if isTrial:
            # row and col sizes
            lsize = rowSizes.sum(0) + colSizes.sum(0)

            # plus borders along axis
            lsize += 2*self.outside + (self.nCols-1, self.nRows-1)*self.inside
            rbox.size = lsize
            return rbox

        else:
            iCellBoxes = self.iterCellBoxes(cells, lbox, rowSizes, colSizes)
            iCells = iter(cells)

            # let cells lay themselves out in their boxes
            for cbox, c in izip(iCellBoxes, iCells):
                c.layoutInBox(cbox)

            # hide cells that have no cbox
            for c in iCells:
                c.layoutInBox(None)

    def iterCellBoxes(self, cells, lbox, rowSizes, colSizes):
        posStart = lbox.pos + lbox.size*self._vaxis
        # come right and down by the outside border
        posStart += self.outside*(1,-1) 
        advCol = self._haxis*self.inside
        advRow = self._vaxis*self.inside

        cellBox = CellBox(posStart, posStart)
        cellPos = cellBox.pos
        posRow = posStart
        for row in rowSizes:
            # adv down by row
            cellPos -= row
            for col in colSizes:
                # yield cell lbox
                cellBox.size = row + col
                yield cellBox

                # adv right by col + inside border
                cellPos += col + advCol

            # adv down by inside border
            cellPos -= advRow
            cellPos[0] = posStart[0]

    def rowColSizesFor(self, cells, lbox):
        vaxis = self._vaxis; haxis = self._haxis
        nRows = self.nRows; nCols = self.nCols

        cellsMinSize = self.cellsMinSize(cells)
        cellsMinSize *= (nCols, nRows)

        # figure out how much room the borders take
        borders = 2*self.outside + (nCols-1, nRows-1)*self.inside

        gridMinSize = borders + cellsMinSize
        lbox.size[:] = numpy.max([lbox.size, gridMinSize], 0)

        # figure out what our starting size minus borders is
        availSize = lbox.size - borders 
        cellSize = (availSize / (nCols, nRows))

        # repeat rowSize nRows times
        rowSizes = empty((nRows, 2), 'f')
        rowSizes[:] = (cellSize*vaxis)
        # repeat colSize nCols times
        colSizes = empty((nCols, 2), 'f')
        colSizes[:] = (cellSize*haxis)
        return rowSizes, colSizes

    def cellsMinSize(self, cells, default=zeros((2,), 'f')):
        nRows = self.nRows; nCols = self.nCols
        minSizes = empty((nRows, nCols, 2), 'f')

        # grab cell info into minSize and weights arrays
        idxWalk = ndindex((nRows, nCols))
        for c, idx in izip(cells, idxWalk):
            minSizes[idx] = (getattr(c, 'minSize', None) or default)

        return minSizes.reshape((-1, 2)).min(0)

