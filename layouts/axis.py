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
    scroll = Vector.property([0.,0.], 'f')
    clip = False

    def countVisibile(self, cells, box):
        return sum(1 for v,c in self.iterCellVisibility(cells, bxo) if v)
    def countInvisibile(self, cells, box):
        return sum(1 for v,c in self.iterCellVisibility(cells, bxo) if not v)
    def iterCellVisibility(self, cells, box):
        lbox = box.copy()

        # determin sizes for cells
        axisSizes, lbox = self.axisSizesFor(cells, lbox)
        iCellBoxes = self.iterCellBoxes(cells, lbox, axisSizes)

        # let cells lay themselves out in their boxes
        for c, cbox in iCellBoxes:
            yield cbox is not None, c

    def layoutCalc(self, cells, box, at=None):
        lbox = box.copy()
        axisSizes, lbox = self.axisSizesFor(cells, lbox)

        # calculate what we used of the box
        axis = self.axis
        lsize = (1-axis)*lbox.size
        # add axisSize and borders along axis
        lsize += axisSizes.sum(0) + axis*(2*self.outside + (len(axisSizes)-1)*self.inside)
        lbox.setSize(lsize, at)
        return lbox

    def layoutCells(self, cells, box):
        lbox = box.copy()

        # determin sizes for cells
        axisSizes, lbox = self.axisSizesFor(cells, lbox)
        iCellBoxes = self.iterCellBoxes(cells, lbox, axisSizes)

        # let cells lay themselves out in their boxes
        for c, cbox in iCellBoxes:
            c.layoutInBox(cbox)

    def axisSizesFor(self, cells, lbox=None):
        if lbox is None:
            lbox = Box()

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

        iterCells = iter(cells)
        clip = self.clip
        if axis[0]: # horizontal
            # let each cell know it's new pos and size
            p0 = lbox.at[0,0] + (1,1)*outside
            pend = lbox.at[1,0] + (-1,1)*outside
            pstart = p0[:]
            p0 += self.scroll

            for asize in axisSizes:
                p1 = p0 + asize + nonAxisSize
                if clip:
                    if (pend-p1)[0] <= 0:
                        break
                    if (pstart-p1)[0] >= 0:
                        yield iterCells.next(), None
                        p0 += asize + axisBorders
                        continue

                cellBox.pv = (p0, p1)
                yield iterCells.next(), cellBox
                p0 += asize + axisBorders

            #p0 += axis*outside

        else: # veritcal 
            # let each cell know it's new pos and size
            p0 = lbox.at[0,1] + (1,-1)*outside
            pend = lbox.at[0,0] + (1,1)*outside
            pstart = p0.copy()
            p0 += self.scroll

            for asize in axisSizes:
                p1 = p0 - asize
                if clip:
                    if (p1-pend)[1] <= 0:
                        break
                    if (p1-pstart)[1] >= 0:
                        yield iterCells.next(), None
                        p0 -= asize + axisBorders
                        continue

                cellBox.pv = (p1, p0 + nonAxisSize)
                yield iterCells.next(), cellBox
                p0 -= asize + axisBorders

            #p0 -= axis*outside

        for cell in iterCells:
            yield cell, None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def cellWeightsMinSizes(self, cells, default=zeros((2,), 'f')):
        minSizes = zeros((len(cells), 2), 'f')
        weights = zeros((len(cells), 2), 'f')

        # grab cell info into minSize and weights arrays
        idxWalk = ndindex(weights.shape[:-1])
        for c, idx in izip(cells, idxWalk):
            weights[idx] = getattr(c, 'weight', default)
            sz = getattr(c, 'minSize', None)
            if sz is None: sz = default
            minSizes[idx] = sz

        return (weights, minSizes)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HorizontalLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([1,0], 'b')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class VerticalLayoutStrategy(AxisLayoutStrategy):
    axis = Vector.property([0,1], 'b')

