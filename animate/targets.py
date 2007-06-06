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

from functools import partial
from operator import setitem, getitem

from TG.metaObserving import OBFactoryMap

from .base import Animation

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimateToTarget(Animation):
    def bind(self, fset, host, key):
        self.host = host
        self.key = key
        self.update = partial(fset, host, key)
        return self

    def endpoints(self, v0, v1):
        if hasattr(v0, 'copy'):
            v0 = v0.copy()
        self.v0 = v0
        if hasattr(v1, 'copy'):
            v1 = v1.copy()
        self.v1 = v1
        return self

    def registryKey(self):
        try: 
            hkey = hash(self.key)
        except TypeError: 
            hkey = id(self.key)
        return ((id(self.host), hkey))

    def animate(self, tv, av, info):
        if av <= 0: 
            return True

        if av < 1: 
            v = (1.0 - av)*self.v0 + (av)*self.v1
        else: v = 0*self.v0 + self.v1

        self.update(v)
        return (av < 1)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimationTargetView(object):
    __slots__ = ['_animator_', '_obj_']

    def __init__(self, animator, obj):
        self._animator_ = animator
        self._obj_ = obj

    def _follow_(self, obj):
        return type(self)(self._animator_, obj)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    def __getattr__(self, key):
        return self._follow_(getattr(self._obj_, key))
    def __setattr__(self, key, v1):
        if key in self.__slots__:
            return object.__setattr__(self, key, v1)

        obj = self._obj_
        v0 = getattr(obj, key)
        return self._animator_.toTarget(v0, v1, setattr, obj, key)

    def __getitem__(self, key):
        return self._follow_(self._obj_[key])
    def __setitem__(self, key, v1):
        obj = self._obj_
        v0 = obj[key]
        return self._animator_.toTarget(v0, v1, setitem, obj, key)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    v = {'cool': 10, 'foo': [0, 2, 4]}

    p = TargetView(v)
    p['cool'] = 20
    p['foo'][1] = 8

    print
    for av in [i*0.1 for i in range(-2, 5)]:
        animateAt(av)
        print '%5s: %r' % (av, v)
    print

    print 'change direction!'
    p['cool'] = 40
    p['foo'][2] = 100

    print
    for av in [i*0.1 for i in range(5, 12)]:
        animateAt(av)
        print '%5s: %r' % (av, v)
    print

