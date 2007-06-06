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

from TG.metaObserving import OBFactoryMap
from .context import AnimationRegistry, AnimationContext
from .targets import AnimateToTarget, AnimationTargetView

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Animators
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnimatorFactoryMap(object):
    pass
afm = AnimatorFactoryMap()
afm.Registry = AnimationRegistry
afm.ToTarget = AnimateToTarget
afm.TargetView = AnimationTargetView

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Animator(AnimationContext):
    afm = afm

    def __repr__(self):
        return "<%s %1.1f>"

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    def timeline(self, iterable=None):
        ar = self.afm.Timeline(self, iterable)
        return self.add(ar)
    def interval(self, td, afn=None):
        ar = self.afm.Interval(self, td, afn)
        return self.add(ar)
    def offset(self, td):
        ar = self.afm.Offset(self, td)
        return self.add(ar)
    delay = offset
    def chain(self, iterable=None):
        ar = self.afm.Chain(self, iterable)
        return self.add(ar)

    def target(self, obj, td=1., afn=None):
        animator = self.interval(td, afn)
        return self.targetView(obj, animator)
    view = target
    def targetView(self, obj, animator):
        return self.afm.TargetView(animator, obj)
afm.Animator = Animator

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Timeline(Animator):
    animate = Animator._animateParallel
    def __init__(self, parentCtx, iterable=None):
        Animator.__init__(self, parentCtx)
        if iterable is not None:
            self.extend(iterable)
afm.Timeline = Timeline

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Chain(Timeline):
    animate = Animator._animateSerial
afm.Chain = Chain

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Interval(Animator):
    animateGroup = Animator._animateParallel
    def __init__(self, parentCtx, td, afn=None):
        Animator.__init__(self, parentCtx)
        self.td = td
        if afn is None:
            self.afn = self.scale
        else: self.afn = afn

    def scale(self, av, dtv, dts):
        return min(1., max(0., dts))

    def animate(self, tv, av, info):
        dtv, dts = self.dtv_dts(tv)
        avp = self.afn(av or 0.0, dtv, dts)
        return self.animateGroup(tv, avp, info)
afm.Interval = Interval

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Offset(Animator):
    def __init__(self, parentCtx, td):
        Animator.__init__(self, parentCtx)
        self.td = td

    def animate(self, tv, av, info):
        dtv = self.dtv(tv)
        if dtv < 0:
            return False
        return self.animateGroup(tv, av, info)
afm.Offset = Offset

