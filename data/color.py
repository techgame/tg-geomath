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

import numpy
from numpy import ndarray, multiply, asarray

from TG.openGL.data import Color # XXX: Temporary use of openGL's color implementation
from .vector import Vector, _VectorIndexSyntaxBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

colorFormatTransforms = {
    ('f', 'f'): None, ('d', 'd'): None,
    ('f', 'd'): None, ('d', 'f'): None,

    ('f', 'B'): 0xff, ('f', 'b'): 0x7f,
    ('d', 'B'): 0xff, ('d', 'b'): 0x7f,
    ('f', 'H'): 0xffff, ('f', 'h'): 0x7fff,
    ('d', 'H'): 0xffff, ('d', 'h'): 0x7fff,
    ('f', 'L'): 0xffffffff, ('f', 'l'): 0x7fffffff,
    ('f', 'I'): 0xffffffff, ('f', 'i'): 0x7fffffff,
    ('d', 'L'): 0xffffffff, ('d', 'l'): 0x7fffffff,
    ('d', 'I'): 0xffffffff, ('d', 'i'): 0x7fffffff,

    ('B', 'b'): 0.5, ('b', 'B'): 2,
    ('H', 'h'): 0.5, ('h', 'H'): 2,
    ('L', 'l'): 0.5, ('l', 'L'): 2,
    ('L', 'i'): 0.5, ('i', 'L'): 2,
    ('I', 'i'): 0.5, ('i', 'I'): 2,

    ('l', 'i'): None, ('i', 'l'): None,
    ('L', 'I'): None, ('I', 'L'): None,

    ('b', 'h'): 0x0101,     ('h', 'b'): 1./0x0100,
    ('b', 'l'): 0x01010101, ('l', 'b'): 1./0x01000000,
    ('b', 'i'): 0x01010101, ('i', 'b'): 1./0x01000000,
    ('h', 'l'): 0x00010001, ('l', 'h'): 1./0x00010000,
    ('h', 'i'): 0x00010001, ('i', 'h'): 1./0x00010000,

    ('B', 'H'): 0x0101,     ('H', 'B'): 1./0x0100,
    ('B', 'L'): 0x01010101, ('L', 'B'): 1./0x01000000,
    ('B', 'I'): 0x01010101, ('I', 'B'): 1./0x01000000,
    ('H', 'L'): 0x00010001, ('L', 'H'): 1./0x00010000,
    ('H', 'I'): 0x00010001, ('I', 'H'): 1./0x00010000,

    ('b', 'H'): 0x0101<<1,     ('H', 'b'): 1./(0x0100<<1),
    ('b', 'L'): 0x01010101<<1, ('L', 'b'): 1./(0x01000000<<1),
    ('b', 'I'): 0x01010101<<1, ('I', 'b'): 1./(0x01000000<<1),
    ('h', 'L'): 0x00010001<<1, ('L', 'h'): 1./(0x00010000<<1),
    ('h', 'I'): 0x00010001<<1, ('I', 'h'): 1./(0x00010000<<1),

    ('B', 'h'): 0x0101>>1,     ('h', 'B'): 1./(0x0100<<1),
    ('B', 'l'): 0x01010101>>1, ('l', 'B'): 1./(0x01000000<<1),
    ('B', 'i'): 0x01010101>>1, ('i', 'B'): 1./(0x01000000<<1),
    ('H', 'l'): 0x00010001>>1, ('l', 'H'): 1./(0x00010000<<1),
    ('H', 'i'): 0x00010001>>1, ('i', 'H'): 1./(0x00010000<<1),
    }
for (l,r), v in colorFormatTransforms.items():
    if v is None: continue
    if (r,l) not in colorFormatTransforms:
        colorFormatTransforms[(r,l)] = 1./v
l=r=v=None
del l, r, v

# add in the max values as a single number
colorFormatTransforms.update({
    'b': 0x7f,
    'B': 0xff,
    'h': 0x7fff,
    'H': 0xffff, 
    'l': 0x7fffffff,
    'L': 0xffffffff, 
    'i': 0x7fffffff,
    'I': 0xffffffff, 
    'f': 1.0,
    'd': 1.0,
    })

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Hex Syntax
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HexSyntax(_VectorIndexSyntaxBase):
    def __str__(self):
        return str(self.vec.tohex())
    __repr__ = __str__

    def __getitem__(self, idx):
        return self.vec[idx].tohex()
    def __setitem__(self, idx, hexData):
        self.vec[idx].setHex(hexData)

class ColorNameSyntax(_VectorIndexSyntaxBase):
    def __setitem__(self, idx, colorName):
        self.vec[idx].setColorName(colorName)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Color Vectors
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ColorVector(Vector):
    byName = {} # filled in later

    def getColorNameSyntax(self):
        return ColorNameSyntax(self)
    def setColorName(self, colorName):
        self.convertFrom(self.byName[colorName])
    name = property(getColorNameSyntax, setColorName)

    def getHex(self):
        return HexSyntax(self)
    def setHex(self, hexData):
        self.convertFrom(self.fromHexRaw(hexData))
    hex = property(getHex, setHex)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    #~ Hex format 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    def getHex(self):
        return HexSyntax(self)
    def setHex(self, hexData):
        self.convertFrom(self.fromHexRaw(hexData))
    hex = property(getHex, setHex)

    def tohex(self, join=' '):
        if self.dtype.char != 'B':
            return self.convert(dtype='B').tohex()

        def vAsHex(v):
            if v.ndim == 1:
                return '#'+v.tostring().encode('hex')
            return asarray(map(vAsHex, v))

        return vAsHex(self)

    @classmethod
    def fromData(klass, data, dtype=None, copy=True, order='C', subok=True, ndmin=1):
        if isinstance(data[0], basestring):
            return klass.fromHex(data, None, dtype)

        return Vector.fromData(data, dtype, copy, order, subok, ndmin)

    @classmethod
    def fromHex(klass, hexData, shape=None, dtype=None):
        colors = klass.fromHexRaw(hexData)
        result = colors.convert(shape, dtype, False)
        if shape is None:
            result = result.squeeze()
        return result

    @classmethod
    def fromName(klass, colorName, shape=None, dtype=None):
        if isinstance(data, basestring):
            data = [data]

        byName = klass.byName
        data = asarray([byName[n] for n in data], 'B')

        result = colors.convert(shape, dtype, False)
        if shape is None:
            result = result.squeeze()
        return result

    #~ raw color transformations ~~~~~~~~~~~~~~~~~~~~~~~~

    hexFormatMap = {}
    for n in range(1, 5):
        hexFormatMap[0, n] = (n, 1, 0x11)
        hexFormatMap[n, n] = (n, 1, 0x11)
        hexFormatMap[n, 2*n] = (n, 2, 1)
        hexFormatMap[0, 2*n] = (n, 2, 1)
    hexFormatMap[0, 2] = (1, 2, 1)

    hexRemapNto4 = {
        1: (lambda r: r*3+(0xff,)),
        2: (lambda r: r[:-1]*3 + r[-1:]),
        3: (lambda r: r+(0xff,)),
        4: (lambda r: r),
        }

    @classmethod
    def fromHexRaw(klass, hexColorData, hexFormatMap=hexFormatMap, hexRemapNto4=hexRemapNto4):
        if isinstance(hexColorData, basestring):
            hexColorData = [hexColorData]

        colorResult = klass.fromShape((len(hexColorData), 4), 'B')
        for i in xrange(len(colorResult)):
            value = hexColorData[i]

            if value[:1] == '#':
                value = value[1:]
            else:
                value = klass.byName.get(value, None)
                if value is not None:
                    colorResult[i] = value
                    continue

                raise ValueError("Expected color string to begin with #: %r" % (value,))

            value = value.strip().replace(' ', ':').replace(',', ':')
            components = value.count(':') 
            if components:
                # add one if no trailing : is found
                components += (not value.endswith(':')) 
                value = value.replace(':', '')
            else: components = 0

            n, f, m = hexFormatMap[components, len(value)]
            value = tuple(value[k:k+f] for k in xrange(0, 4*f, f))

            result = tuple(m*int(e, 16) for e in value if e)
            colorResult[i] = hexRemapNto4[n](result)
        return colorResult

    del hexRemapNto4
    del hexFormatMap


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Color format conversions
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def convert(self, shape=None, dtype=None, copy=True):
        if shape is None: 
            if dtype is None:
                if copy:
                    return self.copy()
                else: return self

            shape = self.shape
        elif dtype is None: 
            dtype = self.dtype

        other = self.fromShape(shape, dtype)
        return self.convertData(self, other)

    def convertAs(self, other):
        return self.convertData(self, other)

    def convertFrom(self, other):
        return self.convertData(other, self)

    @classmethod
    def convertData(klass, src, dst, colorFormatTransforms=colorFormatTransforms):
        if isinstance(dst, (basestring, tuple, numpy.dtype)):
            dst = klass.fromShape(src.shape, dst)
        elif not isinstance(dst, ndarray):
            raise TypeError("Dst parameter expected to be an ndarray or dtype")

        f_src = src.dtype.char
        f_dst = dst.dtype.char
        
        cs_src = src.shape[-1]
        cs_dst = dst.shape[-1]
        if cs_dst > cs_src:
            ci_data = numpy.s_[..., 0:cs_src]
            ci_last = numpy.s_[..., cs_src:]
        else:
            ci_data = numpy.s_[..., 0:cs_dst]
            ci_last = None

        nd_dst = dst.view(ndarray)
        nd_src = src.view(ndarray)

        scale = colorFormatTransforms.get((f_src, f_dst), None)
        if scale is None:
            # just copy the data over
            nd_dst[ci_data] = nd_src[ci_data]

        else: 
            # we need to scale
            if nd_dst.shape == nd_src.shape:
                # we are aligned, so use the ufunc to avoid allocating memory
                multiply(scale, nd_src[ci_data], nd_dst[ci_data])
            else:
                # some sort of broadcast, let numpy do it's magic
                nd_dst[ci_data] = multiply(scale, nd_src[ci_data])

        if ci_last is not None:
            # fill in the last value
            nd_dst[ci_last] = colorFormatTransforms[f_src]

        return dst


#Color = ColorVector # XXX: Temporary use of openGL's color implementation

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def colorVector(data, dtype=None, copy=True, order='C', subok=True, ndmin=1):
    return ColorVector.fromData(data, dtype, copy, order, subok, ndmin)
color = colorVector

def asColorVector(data, dtype=None, copy=False, order='C', subok=True, ndmin=1):
    return ColorVector.fromData(data, dtype, copy, order, subok, ndmin)
asColor = asColorVector

def colorVectorFromUint32(v, hasAlpha=False):
    if hasAlpha:
        r, g, b, a = (v>>24), (v>>16), (v>>8), (v>>0)
    else:
        r, g, b = (v>>16), (v>>8), (v>>0)
        a = 0xff

    return colorVector([r, g, b, a], 'B')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Define colorNameTable now, because it uses colorVectorFromUint32
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from colorNames import colorNameTable
ColorVector.byName = colorNameTable

