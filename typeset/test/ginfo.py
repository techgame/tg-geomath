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

import numpy

from TG.geomath.typeset.typeface import FTTypeface

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    #mosaicSize = (1024, 1024)
    mosaicSize = (2048, 2048)
    fnlist = [
        #'/Library/Fonts/Courier New',
        #'/Library/Fonts/Andale Mono',
        #'/Library/Fonts/Papyrus.dfont',
        #'/Library/Fonts/Zapfino.dfont',
        '/Library/Fonts/Handwriting - Dakota',
        ]

    text = None

    for cs in [
            #12, 16, 24, 32, 36, 48, 60, 64,
            #12, 16, 18, 22, 24, 36, 48, 64, 128
            ]:

        sizes = []
        for fn in fnlist:
            face = FTTypeface(fn, cs)

            if text:
                face.translate(text)
            else: face.loadAll()

            quad = face.sorts['quad']
            sizes.extend(quad[:, 2, :] - quad[:, 0, :])

        sizes = numpy.array(sizes)
        ys = sizes[..., 1]
        maxSize = int(ys.max())
        bins = [0] + [1<<i for i in xrange(4, 16, 1) if (maxSize>>(i-1))]
        bins = numpy.array(bins)

        yi = numpy.digitize(ys, bins)
        hc, l1 = numpy.histogram(ys, bins, normed=False)
        total = float(hc.sum())


        vertical = numpy.zeros(len(bins), 'l')
        for i in xrange(len(bins)):
            w, f = divmod(sizes[yi==i, 0].sum(), mosaicSize[0])
            rows = (w + (1 if f else 0))
            vertical[i] = rows*bins[i]

        vtotal = vertical.sum()

        print
        print 'Pts:', cs, 'height: %d (%r)' % (vtotal, vtotal < mosaicSize[1]), 'mosaic:', mosaicSize
        cw = 100.0 * total / hc.max()
        for i in range(len(l1)):
            print '%6.2f: %4d, %8.6f | %s' % (l1[i], hc[i], hc[i]/total, (hc[i]/total)*cw*'#')
        print

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    main()

