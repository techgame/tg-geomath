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

import time

from TG.geomath.data.box import Box
from TG.geomath.layouts.cells import *
from TG.geomath.layouts.axisLayout import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

box = Box((0,0), (1000, 1000))

def runAxisLayout():
    cells = [
        Cell(0, 200),
        MaxSizeCell(1, 200, 300),
        Cell(1, 200),
        ]

    vl = VerticalLayoutStrategy()

    if 1:
        vl.inside = 10
        vl.outside = 50, 50

    if 1:
        for p in xrange(2):
            lb = vl.layout(cells, box, not p%2)
            print
            print 'box:', box.tolist()
            if lb is not None:
                print '  layout:', lb.tolist()
            for i, c in enumerate(cells):
                print '    cell %s:' % i, c.box.tolist()
            print

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def runAxisTimiing(n=100):
    cells = [
        Cell(0, 200),
        MaxSizeCell(1, 200, 300),
        Cell(1, 200),
        ]

    vl = VerticalLayoutStrategy()

    if 1:
        vl.inside = 10
        vl.outside = (50, 50)

    box.size *= 5
    cells *= 10
    cn = max(1, len(cells)*n)

    if 1:
        s = time.time()
        for p in xrange(n):
            vl.layout(cells, box, False)
        dt = time.time() - s
        print '%r time: %5s cn/s: %5s pass/s: %5s' % ((n,cn), dt, cn/dt, n/dt)

    if 1:
        s = time.time()
        for p in xrange(n):
            vl.layout(cells, box, True)
        dt = time.time() - s
        print '%r time: %5s cn/s: %5s pass/s: %5s' % ((n,cn), dt, cn/dt, n/dt)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    if 1:
        runAxisLayout()

    # timing analysis
    if 1:
        runAxisTimiing()

