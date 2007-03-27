#!/usr/bin/env python
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

from ..raw import gl, glext
from ..data.texture import Texture, TextureCoordArray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FontTextureBase(Texture):

    texParams = Texture.texParams + [
            ('format', gl.GL_ALPHA),

            ('wrap', gl.GL_CLAMP),
            #('genMipmaps', True),
            ('magFilter', gl.GL_LINEAR),
            ('minFilter', gl.GL_LINEAR),#_MIPMAP_LINEAR),
            ]
    dataFormat = gl.GL_ALPHA
    dataType = gl.GL_UNSIGNED_BYTE

    texCoordScale = TextureCoordArray([[0., 1.], [1., 1.], [1., 0.], [0., 0.]], '2f')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def createMosaic(self, mosaicSize):
        self.select()
        size = self.validSizeForTarget(mosaicSize+(0,))
        data = self.blankImage2d(size=size, format=self.dataFormat, dataType=self.dataType)
        data.newPixelStore(alignment=1, rowLength=0)
        self._mosaicData = data
        return data

    def getMaxMosaicSize(self): 
        return self.getMaxTextureSize()

    def renderGlyph(self, glyph, pos, size):
        texData = self._mosaicData

        glyph.render()

        texData.texCData(glyph.bitmap.buffer, dict(rowLength=glyph.bitmap.pitch))
        texData.setSubImageOn(self, pos=pos, size=size)

        texCoords = texData.pos[:2] + (texData.size[:2]*self.texCoordScale)
        return self.texCoordsFor(texCoords)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FontTextureRect(FontTextureBase):
    texParams = FontTextureBase.texParams + [('target', glext.GL_TEXTURE_RECTANGLE_ARB)]

class FontTexture2d(FontTextureBase):
    texParams = FontTextureBase.texParams + [('target', gl.GL_TEXTURE_2D)]

