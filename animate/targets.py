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

from operator import setitem, getitem

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimateTarget(object):
    def __init__(self, target, key, v0, v1, updateFn):
        self.target = target
        self.key = key
        self.updateFn = updateFn
        if hasattr(v0, 'copy'):
            v0 = v0.copy()
        self.v0 = v0
        self.v1 = v1

    def register(self, bAdd=True):
        if bAdd:
            animateCollection[self.akey()] = self
        else:
            animateCollection.pop(self.akey(), None)

    def akey(self):
        try: hkey = hash(self.key)
        except TypeError: hkey = id(self.key)
        return (id(self.target), hkey)

    def __call__(self, t):
        if t <= 0: 
            return
        elif t < 1: 
            v = (1-t)*self.v0 + (t)*self.v1
        else: 
            v = self.v1
            self.register(False)

        self.updateFn(self.target, self.key, v)
        return self.target

animateCollection = {}
def animateAt(t):
    for e in animateCollection.values():
        e(t)

class TargetView(object):
    __slots__ = ['host']
    AnimateTarget = AnimateTarget

    def __init__(self, host):
        self.host = host

    @classmethod
    def new(klass, host):
        return klass(host)

    def addTarget(self, target, key, v0, v1, updateFn):
        target = self.AnimateTarget(target, key, v0, v1, updateFn)
        target.register(True)
        return target

    def __getattr__(self, key):
        return self.new(getattr(self.host, key))
    def __setattr__(self, key, v1):
        if key in self.__slots__:
            return object.__setattr__(self, key, v1)

        host = self.host
        v0 = getattr(host, key)
        return self.addTarget(host, key, v0, v1, setattr)

    def __getitem__(self, key):
        return self.new(self.host[key])
    def __setitem__(self, key, v1):
        host = self.host
        v0 = host[key]
        return self.addTarget(host, key, v0, v1, setitem)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    v = {'cool': 10, 'foo': [0, 2, 4]}

    p = TargetView(v)
    p['cool'] = 20
    p['foo'][1] = 8

    print
    for t in [i*0.1 for i in range(-2, 5)]:
        animateAt(t)
        print '%5s: %r' % (t, v)
    print

    print 'change direction!'
    p['cool'] = 40
    p['foo'][2] = 100

    print
    for t in [i*0.1 for i in range(5, 12)]:
        animateAt(t)
        print '%5s: %r' % (t, v)
    print

