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
import string

import numpy

from TG.geomath.typeset.mosaic import MosaicPageArena
from TG.geomath.typeset.typeface import FTTypeface

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    #mosaicSize = (1<<11, 1<<11)
    #mosaicSize = (1<<10, 1<<10)
    mosaicSize = (1<<11, 1<<8)

    fnlist = [
        '/System/Library/Fonts/OsakaMono.dfont',
        '/Library/Fonts/BiauKai.dfont',
        '/Library/Fonts/Apple LiSung Light.dfont',
        '/Library/Fonts/Courier New',
        '/Library/Fonts/Andale Mono',
        '/Library/Fonts/Cracked',
        '/Library/Fonts/Baskerville.dfont',
        '/Library/Fonts/Arial',
        '/Library/Fonts/Papyrus.dfont',
        '/Library/Fonts/Handwriting - Dakota',
        #'/Library/Fonts/Zapfino.dfont',
        ]
    fn = fnlist[0]

    charSizes = [
        #10, 12, 14, 16, 18, 24, 32, 
        32
        #36, 48, 60, 64, 
        #72, 80, 84, 96
        ]

    arena = MosaicPageArena(mosaicSize)

    verticalText = u'\u6a19\u6e96\u8a9e'
    horizontalText = string.printable

    print
    print "compiling arena for:"
    print fnlist
    print charSizes
    print

    for cs in charSizes:
        for fn in fnlist:
            face = FTTypeface(fn, cs)
            if 'vertical' in face._ftFace.flags:
                text = verticalText
            else:
                text = horizontalText

            sorts = face.translate(text)
            pageEntries = arena[sorts]

    print 'arena entries:'
    print len(arena._entries)
    print
    for i, page in enumerate(arena.pages):
        page.asImage(None, 'page-%d.png' % (i,))
        print

        total = page.page.nbytes
        waste = numpy.sum(page.waste)/float(total)
        density = 1. - waste

        print 'page:', i, 'density:', density
        for k, v in page.blocks.items():
            print '  %3d: %r' % (k, [(p[1], s[0]) for p,s in v])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    main()

