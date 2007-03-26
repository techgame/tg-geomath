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

box = Box()

def runGridLayout(nRows=2, nCols=4, excess=4):
    gl = GridLayoutStrategy(nRows, nCols)
    cells = [Cell((i%2, (i//4)%2), (200, 200)) for i in xrange(nRows*nCols+excess)]

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    if 1:
        runGridLayout()

