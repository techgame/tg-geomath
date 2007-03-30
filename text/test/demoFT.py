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
    ftFace = FreetypeFace('/Library/Fonts/Andale Mono')
    ftFace.setPixelSize(2*72)

    ftLoader = FreetypeLoader()
    face1 = ftLoader.compile(ftFace)

    ci = face1.indexesOf('Shane')
    print ci
    print (1*face1.verticies[ci[0]]).astype('i')

    ftFace.setCharSize(2*72, 96)
    face2 = ftLoader.compile(ftFace)

    ci = face2.indexesOf('Shane')
    print ci
    print (1*face2.verticies[ci[0]]).astype('i')


if __name__=='__main__':
    main()

