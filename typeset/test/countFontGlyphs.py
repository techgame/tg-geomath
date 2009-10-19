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

import os
import numpy
from TG.ext.freetype2.face import FreetypeFace, FreetypeException

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    r = []

    for path in ['/Library/Fonts', '/System/Library/Fonts']:
        for fontFn in os.listdir(path):
            fontPath = os.path.join(path, fontFn) 
            try: ftFace = FreetypeFace(fontPath)
            except FreetypeException, e: 
                continue

            ng = ftFace.numGlyphs
            if ng < 2000:
                r.append(ng)
            else:
                print fontFn, ng

    r = numpy.array(sorted(r))
    h, l = numpy.histogram(r)
    print 'histogram:'
    print h
    print

    print len(r), [r.min(), r.mean(), r.max()]
    print
    #for e in r:
    #    print e*32
