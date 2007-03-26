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

from TG.geomath.layouts.cells import *
from TG.geomath.layouts.gridLayout import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

box = Box((0,0), (1000, 1000))

def runGridLayout(nRows=2, nCols=4, excess=4):
    gl = GridLayoutStrategy(nRows, nCols)
    cells = [Cell((i%2, (i//4)%2), (100, 100)) for i in xrange(nRows*nCols+excess)]

    if 1:
        gl.inside = 10
        gl.outside = (50, 50)

    for p in xrange(2):
        lb = gl.layout(cells, box, not p%2)
        print
        print 'box:', box.tolist()
        if lb is not None:
            print '  layout:', lb.tolist()
        for i, c in enumerate(cells):
            print '    cell %s:' % i, c.box.tolist()
        print

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def runGridTiming(n=100):
    box = Box((0,0), (1000, 1000))
    box.size *= (5, 2)

    nRows, nCols = 10, 8
    excess = 0

    gl = GridLayoutStrategy(nRows, nCols)
    cells = [Cell((i%2, (i//4)%2), (100, 100)) for i in xrange(nRows*nCols+excess)]

    cn = max(1, len(cells)*n)

    if 1:
        gl.inside = 10
        gl.outside = (50, 50)

    if 1:
        s = time.time()
        for p in xrange(n):
            gl.layout(cells, box, False)
        dt = time.time() - s
        print '%r time: %5s cn/s: %5s pass/s: %5s' % ((n, nRows, nCols, cn), dt, cn/dt, n/dt)

    if 1:
        s = time.time()
        for p in xrange(n):
            gl.layout(cells, box, True)
        dt = time.time() - s
        print '%r time: %5s cn/s: %5s pass/s: %5s' % ((n, nRows, nCols, cn), dt, cn/dt, n/dt)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    if 1:
        runGridLayout()

    # timing analysis
    if 1:
        runGridTiming()

