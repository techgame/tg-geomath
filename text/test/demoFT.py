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

from TG.geomath.text.freetypeFontLoader import FreetypeLoader, FreetypeFace

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    pointSize = 16
    dpi = 72
    multiple = 2

    ftFace = FreetypeFace('/Library/Fonts/Andale Mono')
    ftFace.setCharSize(pointSize, dpi)

    ftLoader = FreetypeLoader()
    face1 = ftLoader.compile(ftFace)

    f1ci = face1.indexesOf('T')
    ci1 = (1*face1.verticies[f1ci[0]])
    bi1 = (1*face1.bitmapSize[f1ci[0]])

    ftFace.setCharSize(pointSize*multiple, dpi)
    face2 = ftLoader.compile(ftFace)

    f2ci = face2.indexesOf('T')
    ci2 = (1*face2.verticies[f2ci[0]])
    bi2 = (1*face2.bitmapSize[f2ci[0]])

    cw1 = ci1[1] - ci1[3]
    cw2 = ci2[1] - ci2[3]

    if 1:
        print cw1
        print cw2

    if 0:
        print ci1
        print ci2

    if 1:
        print 'bitmap sizes:'
        print bi1, bi2
        print (bi2.astype('f')/bi1) - multiple

    if 1:
        print 'widths:'
        print ((cw2/multiple)-cw1)
        print ((cw2)-(cw1*multiple))

    if 0:
        print ((ci2/multiple)-ci1)
        print ((ci2)-(ci1*multiple))


if __name__=='__main__':
    main()

