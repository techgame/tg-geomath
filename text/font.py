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

from itertools import izip
from numpy import ndarray, float32, asarray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FaceObject(object):
    charMap = None
    advance = None
    kerningMap = None

    def indexesOf(self, text):
        return asarray(map(self.charMap.get, text), 'H')

    def kernOffsets(self, indexes):
        km = self.kerningMap
        if km is None or len(indexes) < 2:
            return None
        
        k0 = km[None]
        kernOffsets = empty((len(indexes),)+k0.shape, k0.dtype)
        kernOffsets[0] = k0

        lrIndexes = izip(indexes[:-1], indexes[1:])
        kernOffsets[1:] = [km.get(lr, k0) for lr in lrIndexes]
        return kernOffsets
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLoaderStart(self):
        pass

    def _onLoaderFinish(self):
        assert self.charMap is not None
        assert self.verticies is not None
        assert self.advance is not None
        assert self.lineAdvance is not None

