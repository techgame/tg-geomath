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

from ..raw import gl

from ..data.vertexArrays import VertexArray
from ..data.interleavedArrays import InterleavedArray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FontGeometryArray(InterleavedArray):
    drawMode = gl.GL_QUADS
    gldtype = InterleavedArray.gldtype.copy()
    gldtype.setDefaultFormat(gl.GL_T2F_V3F)

class FontAdvanceArray(VertexArray):
    gldtype = VertexArray.gldtype.copy()
    gldtype.setDefaultFormat('3f')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FontTextData(object):
    FontGeometryArray = FontGeometryArray
    FontAdvanceArray = FontAdvanceArray

    def __init__(self, text, font=None):
        if font is not None:
            self.setFont(font)
        self.text = text

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _font = None
    def getFont(self):
        return self._font
    def setFont(self, font):
        if isinstance(self, type):
            self._font = font
        else:
            self._font = font
            self.recompile()
    font = property(getFont, setFont)

    setClassFont = classmethod(setFont)

    @classmethod
    def factoryUpdateFor(klass, font):
        if font is klass.font:
            klass.setClassFont(font)
            return klass
        else:
            subklass = type(klass)(klass.__name__+'_T_', (klass,), {})
            subklass.setClassFont(font)
            return subklass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _text = ""
    def getText(self):
        return self._text
    def setText(self, text):
        self._text = text
        self.recompile()
    text = property(getText, setText)

    def __nonzero__(self):
        return bool(self._text)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recompile(self):
        if self._font is not None:
            self._xidx = self._font.translate(self._text or '')
        self._geometry = None
        self._advance = None
        self._offset = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getTexture(self):
        return self._font.texture
    texture = property(getTexture)

    _geometry = None
    def getGeometry(self):
        r = self._geometry
        if r is None:
            r = self._font.geometry[self._xidx]
            self._geometry = r
        return r
    geometry = property(getGeometry)

    def getLineAdvance(self):
        return self._font.lineAdvance
    lineAdvance = property(getLineAdvance)

    _advance = None
    def getAdvance(self):
        r = self._advance
        if r is None:
            r = self._font.advance[[0]+self._xidx]
            k = self._font.kernIndexes(self._xidx)
            if k is not None:
                r[1:-1] += k
            self._advance = r
        return r
    advance = property(getAdvance)

    _offset = None
    def getOffset(self):
        r = self._offset
        if r is None:
            r = self.getAdvance().cumsum(0)
            self._offset = r
        return r
    offset = property(getOffset)

