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

from numpy import ndarray, float32, asarray

from . import fontData
from . import fontTexture

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Font(object):
    FontMosaicImage = fontTexture.FontTextureRect
    FontTextData = fontData.FontTextData
    FontGeometryArray = fontData.FontGeometryArray
    FontAdvanceArray = fontData.FontAdvanceArray

    mosaicImage = None

    charMap = None
    geometry = None
    advance = None
    kerningMap = None

    pointSize = FontAdvanceArray([1./64., 1./64., 1./64.])[0]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Text translation
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def textData(self, text=''):
        raise RuntimeError("Font has not been loaded")

    def translate(self, text):
        return map(self.charMap.get, text)

    def kernIndexes(self, idx, default=asarray([0., 0., 0.], 'f')):
        km = self.kerningMap
        if not km or len(idx) < 2:
            return None
        
        r = asarray([km.get(e, default) for e in zip(idx, idx[1:])], float32)
        return r.reshape((-1, 1, 3))
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLoaderStart(self):
        self.textData = None

    def _onLoaderFinish(self):
        self.textData = self.FontTextData.factoryUpdateFor(self)
        self.texture = self.mosaicImage

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FontRect(Font):
    FontMosaicImage = fontTexture.FontTextureRect

class Font2d(Font):
    FontMosaicImage = fontTexture.FontTexture2d

