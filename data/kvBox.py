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

from TG.kvObserving import KVObject
from .dataDescriptors import kvDataProperty
from .import box

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVBox(KVObject, box.Box):
    @property
    def _data_changed_(self):
        self.kvpub('*')

    def _onViewDataChange(self, kvhost, key):
        self.kvpub('*')

    @classmethod
    def new(klass):
        self = klass.__new__(klass)
        klass.observerNotifyInit(self)
        return self

    def viewOf(self, other, dref=None, dim=None):
        other.kvpub.add('*', self._onViewDataChange)
        if dref is None:
            dref = other.getDataRef()
        if dim: 
            dref = dref[..., :dim]
        self.setDataRef(dref)

KVBox.property = classmethod(kvDataProperty)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVCenterBox(KVBox):
    at_rel_default = box.CenterBox.at_rel_default

