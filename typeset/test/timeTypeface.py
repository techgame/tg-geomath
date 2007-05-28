#!/usr/bin/env python
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys, time
from TG.geomath.typeset.typesetter import TypeSetter
from TG.geomath.typeset.typeface import FTTypeface

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    fn = '/Library/Fonts/Zapfino.dfont'
    face = FTTypeface(fn, 32)

    print face.sorts.dtype.itemsize

    text = open(__file__, 'rU').read()
    text *= 10

    Mbps = 1./(1<<17)
    print
    print 'Translate Text:'
    for x in xrange(5):
        t0 = time.time()
        sorts = face.translate(text)
        t1 = time.time()

        assert len(text) == len(sorts)
        offset = sorts['offset'][-1].sum()
        advance = sorts['advance'].mean(0).sum()
        print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d, offset: %d, mean adv: %1.2f' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), text.count('\n'), offset, advance)
    print

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    main()

