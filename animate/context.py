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
        return True, animation.animate

    def unregister(self, animation, context):
        key = self.keyFor(animation)
        if key is None:
            return False
        entry = self.registry.get(key)
        if entry is None:
            return False

        aref, cref = entry
        if context is not cref():
            return False

        del self.registry[key]
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
        isAnimator, animate = self.registry.register(animation, self)
        if isAnimator:
            animation.initAnimation(self)
        self._animateList.append(animate)
        return animation
    def addFn(self, fn, incInfo=False):
        if incInfo:
            lfn = lambda tv, av, i: fn(i)
        else: lfn = lambda tv, av, i: fn()

        self._animateList.append(lfn)
        return fn

    def extend(self, iterable):
        for animation in iterable:
            self.add(animation)

    def remove(self, animation):
        self.registry.unregister(animation, self)
        self.discard(animation)
    def discard(self, animation):
        try: self._animateList.remove(animation)
        except LookupError: return False
        except ValueError: return False
        else: return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def animate(self, tv, av, info):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def _animateParallel(self, tv, av, info):
        self.tv = tv
        alist = self._animateList
        for idx, animate in enumerate(alist):
            # if animate is done
            if not animate(tv, av, info):
                alist[idx] = None

        alist[:] = [a for a in alist if a is not None]
        return len(alist)
    
    def _animateSerial(self, tv, av, info):
        self.tv = tv
        alist = self._animateList
        for idx, animate in enumerate(alist):
            # if animate is done
            if not animate(tv, av, info):
                alist[idx] = None
            else: break

        alist[:] = [a for a in alist if a is not None]
        return len(alist)

    _animateGroup = _animateParallel

