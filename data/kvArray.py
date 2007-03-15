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

from numpy import ndarray
from TG.kvObserving import KVObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVArray(ndarray, KVObject):
    __array_priority__ = -5

    def __setitem__(self, i, item): 
        list.__setitem__(self, i, item)
        self.kvpub('*')
    def __delitem__(self, i): 
        list.__delitem__(self, i)
        self.kvpub('*')
    def __setslice__(self, i, j, other):
        list.__setslice__(self, i, j, other)
        self.kvpub('*')
    def __delslice__(self, i, j):
        list.__delslice__(self, i, j)
        self.kvpub('*')

