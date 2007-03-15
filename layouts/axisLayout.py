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
#~ Axis Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AxisLayoutStrategy(BaseLayoutStrategy):
    _nAdjustTries = 3
    axis = Vector.property([0,0], '2b')

    def layout(self, cells, box, isTrial=False):
        if not cells:
            return box.pos.copy(), 0*box.size

        box = box.copy()

        # determin visible cells
        visCells = self.cellsVisible(cells)

        # determin sizes for cells
        axisSizes = self.axisSizesFor(visCells, box, isTrial)

        if not isTrial:
            iCells = iter(visCells)
            iCellBoxes = self.iterCellBoxes(visCells, box, axisSizes, isTrial)

            # let cells lay themselves out in their boxes
            for cbox, c in izip(iCellBoxes, iCells):
                c.layoutInBox(cbox)

            # hide cells that have no box
            for c in iCells:
                c.layoutHide()

        return self.layoutBox(visCells, box, axisSizes, isTrial)

    def axisSizesFor(self, cells, box, isTrial=False):
        # determin minsize
        axis = self.axis
        weights, axisSizes = self.cellsStats(cells)

        minNonAxisSize = (1-axis)*(axisSizes.max() + 2*self.outside)
        box.size[:] = numpy.max([box.size, minNonAxisSize], 0)
        weights *= axis
        axisSizes *= axis

        # calculate the total border size
        borders = axis*(2*self.outside + (len(cells)-1)*self.inside)
        availSize = axis*box.size - borders

        # now remove all the minSize items
        availSize -= axisSizes.sum(0)

        # if we have any space left over, distribute to weighted items
        if (availSize >= 0).all():
            weightSum = weights.sum()
            if weightSum > 0:
                axisSizes += weights*availSize/weightSum

        # allow the cells to negotiate space and adjust to it
        axisSizes = self.axisSizeAdjust(cells, box, weights, axisSizes, isTrial)
        return axisSizes

    def axisSizeAdjust(self, cells, box, weights, axisSizes, isTrial=False):
        weightSum = weights.sum()

        for x in xrange(self._nAdjustTries):
            # allow cells to adjust for maxsize, rounding, etc
            adjSizes = self.cellsAdjustedSize(cells, axisSizes, isTrial)
            idxAdj = (adjSizes != 0).any(-1)
            if not idxAdj.any():
                # if none changed, we are done
                break

            # adjust as requested
            axisSizes -= adjSizes

            # repartition our adjSize to new weighted ones
            availSize = adjSizes.sum(0)

            # remove those who changed the size from the weights
            weightSum -= weights[idxAdj].sum()
            weights[idxAdj] = 0

            if weightSum > 0:
                # distributed the available size to the remaining weighted items
                axisSizes += weights*availSize/weightSum
            else:
                # if there are no more items to reweight, then we are done
                break

        return axisSizes

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def iterCellBoxes(self, cells, box, axisSizes, isTrial=False):
        axis = self.axis
        outside = self.outside
        nonAxisSize = (1-axis)*(box.size - 2*outside)
        pos = box.pos + outside
        axisBorders = axis*self.inside

        cellBox = Rect()

        # let each cell know it's new pos and size
        for asize in axisSizes:
            cellBox.pos[:] = pos
            cellBox.size[:] = asize + nonAxisSize
            yield cellBox

            pos += asize + axisBorders
        pos -= axisBorders

    def layoutBox(self, visCells, box, axisSizes, isTrial=False):
        axis = self.axis

        lbox = box.copy()
        lsize = lbox.size
        lsize *= (1-axis)
        # add axisSize and borders along axis
        lsize += axisSizes.sum(0) + axis*(2*self.outside + (len(axisSizes)-1)*self.inside)
        return lbox

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cellsStats(self, cells, default=zeros((2,), 'f')):
        minSizes = empty((len(cells), 2), 'f')
        weights = empty((len(cells), 2), 'f')

        # grab cell info into minSize and weights arrays
        idxWalk = ndindex(weights.shape[:-1])
        for c, idx in izip(cells, idxWalk):
            weights[idx] = (getattr(c, 'weight', None) or default)
            minSizes[idx] = (getattr(c, 'minSize', None) or default)

        return (weights, minSizes)

    def cellsAdjustedSize(self, cells, axisSizes, isTrial=False, default=zeros((2,), 'f')):
        adjSizes = empty_like(axisSizes)
        axis = self.axis
        for c, axSize, adSize in zip(cells, axisSizes, adjSizes):
            adjustSize = getattr(c, 'adjustSize', None)
            if adjustSize is not None:
                adSize[:] = axSize - axis*adjustSize(axSize)
            else: adSize[:] = default
        return adjSizes

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HorizontalLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([1,0], '2b')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class VerticalLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([0,1], '2b')

