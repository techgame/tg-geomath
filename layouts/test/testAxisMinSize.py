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
from TG.geomath.layouts.axisLayout import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

box = Box()

def runAxisLayout():
    cells = [
        Cell(0, 200),
        MaxSizeCell(1, 200, 300),
        Cell(1, 200),
        ]

    vl = VerticalLayoutStrategy()

    if 1:
        vl.inside = 10
        vl.outside = (50, 50)

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
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    runAxisLayout()

