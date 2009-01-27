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

import weakref
from .base import Animation

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Registry
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimationRegistry(object):
    def __init__(self):
        self.registry = {}

    def keyFor(self, animation):
        key = getattr(animation, 'registryKey', None)
        if key is not None:
            return key()

    def register(self, animation, context):
        key = self.keyFor(animation)

        if key is None:
            return False, animation

        oldEntry = self.registry.get(key)
        self.registry[key] = (animation.ref(), context.ref())
        if oldEntry is not None:
            self.notifyReplaced(*oldEntry)
        return key, animation.animate

    def unregister(self, key, animation, context):
        if key is None:
            key = self.keyFor(animation)

        entry = self.registry.pop(key, None)
        if entry is None:
            return False

        aref, cref = entry
        self.notifyReplaced(aref, cref)
        return True

    def notifyReplaced(self, aref, cref):
        animation = aref()
        if animation is None: 
            return

        context = cref()
        if context is None: 
            return

        context.onReplaced(animation)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimationContext(Animation):
    def __init__(self, parentCtx=None):
        if parentCtx is not None:
            self.initContext(parentCtx.registry)

    def initContext(self, registry=None):
        self.registry = registry 
        self._animateList = []

    def ref(self, cb=None):
        return weakref.ref(self, cb)

    def onReplaced(self, animation):
        self.discard(animation)

    def __len__(self):
        return len(self._animateList)

    def __iadd__(self, animation):
        self.add(animation)
        return self
    def __isub__(self, animation):
        self.remove(animation)
        return self

    def add(self, animation):
        key, animate = self._register(animation)
        if key:
            animation.initAnimation(self)
        self._animateList.append((key, animate))
        return animation
    def addFn(self, fn, incInfo=False):
        if incInfo:
            lfn = lambda tv, av, i: fn(i)
        else: lfn = lambda tv, av, i: fn()

        self._animateList.append((None, lfn))
        return fn

    def extend(self, iterable):
        for animation in iterable:
            self.add(animation)

    def remove(self, animation):
        key = self._keyFor(animation)
        if key is None:
            for fn, key in self._animateList:
                if animation == fn:
                    break


        self._animateList.remove((key, animation))
        self._unregister(animation, key)
        return True

    def clear(self):
        animateList = self._animateList
        self._animateList = []

        for (key, animation) in animateList:
            self._unregister(animation, key)

    def discard(self, animation):
        try: 
            self.remove(animation)
        except LookupError: return False
        except ValueError: return False
        else: return True

    def _keyFor(self, animation):
        return self.registry.keyFor(animation)
    def _register(self, animation):
        return self.registry.register(animation, self)
    def _unregister(self, animation, key):
        return self.registry.unregister(key, animation, self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def animate(self, tv, av, info):
        raise NotImplementedError('Subclass Responsibility: %r' % (self.__class__,))

    def _animateParallel(self, tv, av, rmgr):
        self.tv = tv
        alist = self._animateList
        if not len(alist): return 0

        for idx, (key, animate) in enumerate(alist):
            # if animate is done
            if not animate(tv, av, rmgr):
                self._unregister(animate, key)
                alist[idx] = None

        alist[:] = [a for a in alist if a is not None]
        return len(alist)
    
    def _animateSerial(self, tv, av, rmgr):
        self.tv = tv
        alist = self._animateList
        if not len(alist): return 0

        for idx, (key, animate) in enumerate(alist):
            # if animate is done
            if not animate(tv, av, rmgr):
                self._unregister(animate, key)
                alist[idx] = None
            else: break

        alist[:] = [a for a in alist if a is not None]
        return len(alist)

    _animateGroup = _animateParallel

