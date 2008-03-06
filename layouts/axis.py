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

from ..data.box import Box
from ..data.vector import Vector

from .basic import BaseLayoutStrategy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Axis Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AxisLayoutStrategy(BaseLayoutStrategy):
    axis = Vector.property([0,0], 'b')
    clip = False

    def layoutCalc(self, cells, box):
        lbox = box.copy()
        axisSizes, lbox = self.axisSizesFor(cells, lbox)

        # calculate what we used of the box
        axis = self.axis
        lsize = (1-axis)*lbox.size
        # add axisSize and borders along axis
        lsize += axisSizes.sum(0) + axis*(2*self.outside + (len(axisSizes)-1)*self.inside)
        lbox.size = lsize
        return lbox

    def layoutCells(self, cells, box):
        lbox = box.copy()

        # determin sizes for cells
        axisSizes, lbox = self.axisSizesFor(cells, lbox)

        iCellBoxes = self.iterCellBoxes(cells, lbox, axisSizes)
        iCells = iter(cells)

        # let cells lay themselves out in their boxes
        for cbox, c in izip(iCellBoxes, iCells):
            c.layoutInBox(cbox)

        # hide cells that have no cbox
        for c in iCells:
            c.layoutInBox(None)

    def axisSizesFor(self, cells, lbox):
        # determin minsize
        axis = self.axis
        weights, axisSizes = self.cellWeightsMinSizes(cells)

        if axisSizes.size > 0:
            minNonAxisSize = axisSizes.max(0)
        else: minNonAxisSize = 0
        minNonAxisSize = (1-axis)*(minNonAxisSize + 2*self.outside)
        lbox.size = numpy.max([lbox.size, minNonAxisSize], axis=0)
        weights *= axis
        axisSizes *= axis

        # calculate the total border size
        borders = axis*(2*self.outside + (len(cells)-1)*self.inside)
        availSize = axis*lbox.size - borders

        # now remove all the minSize items
        availSize -= axisSizes.sum(0)

        # if we have any space left over, distribute to weighted items
        if (availSize >= 0).all():
            weightSum = weights.sum()
            if weightSum > 0:
                axisSizes += (weights*availSize)/weightSum

        return axisSizes, lbox

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def iterCellBoxes(self, cells, lbox, axisSizes):
        axis = self.axis
        outside = self.outside
        nonAxisSize = (1-axis)*(lbox.size - 2*outside)
        axisBorders = axis*self.inside

        cellBox = Box()

        clip = self.clip
        if axis[0]: # horizontal
            # let each cell know it's new pos and size
            p0 = lbox.at[0,0] + (1,1)*outside
            pend = lbox.at[1,0] + (-1,1)*outside

            for asize in axisSizes:
                p1 = p0 + asize + nonAxisSize
                if clip and (pend-p1)[0] <= 0:
                    break

                cellBox.pv = (p0, p1)
                yield cellBox
                p0 += asize + axisBorders

            #p0 += axis*outside

        else: # veritcal 
            # let each cell know it's new pos and size
            p0 = lbox.at[0,1] + (1,-1)*outside
            pend = lbox.at[0,0] + (1,1)*outside

            for asize in axisSizes:
                p1 = p0 - asize
                if clip and (p1-pend)[1] <= 0:
                    break

                cellBox.pv = (p1, p0 + nonAxisSize)
                yield cellBox
                p0 -= asize + axisBorders

            #p0 -= axis*outside

    debug = False
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cellWeightsMinSizes(self, cells, default=zeros((2,), 'f')):
        minSizes = zeros((len(cells), 2), 'f')
        weights = zeros((len(cells), 2), 'f')

        # grab cell info into minSize and weights arrays
        idxWalk = ndindex(weights.shape[:-1])
        for c, idx in izip(cells, idxWalk):
            weights[idx] = getattr(c, 'weight', default)
            minSizes[idx] = getattr(c, 'minSize', default)

        return (weights, minSizes)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HorizontalLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([1,0], 'b')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class VerticalLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([0,1], 'b')

