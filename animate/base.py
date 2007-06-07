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
from ..data.vector import DataHostObject, Vector

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Animation Base  Object
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Animation(DataHostObject):
    timebase = Vector.property([0, 1, 0], dtype='f')

    def initAnimation(self, parent):
        self.timebase[:] += parent.tv

    def get_t0(self): return self.timebase[0]
    def set_t0(self, t0): self.timebase[0] = t0
    t0 = property(get_t0, set_t0)

    def get_t1(self): return self.timebase[1]
    def set_t1(self, t1): self.timebase[1] = t1
    t1 = property(get_t1, set_t1)

    def get_td(self): 
        timebase = self.timebase
        return timebase[1] - timebase[0]
    def set_td(self, td): 
        timebase = self.timebase
        timebase[1] = timebase[0] + td
    td = property(get_td, set_td)

    def get_tv(self): return self.timebase[2]
    def set_tv(self, tv): self.timebase[2] = tv
    tv = property(get_tv, set_tv)

    def dtv(self, tv=None):
        timebase = self.timebase
        if tv is None:
            tv = timebase[2]
        else: timebase[2] = tv
        t0 = timebase[0]
        return tv-t0
    def dtv_dts(self, tv=None):
        timebase = self.timebase
        if tv is None:
            tv = timebase[2]
        else: timebase[2] = tv

        t0 = timebase[0]
        t1 = timebase[1]
        dv = (tv-t0)
        return dv, dv/(t1-t0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def ref(self, cb=None):
        return weakref.ref(self, cb)
    def registryKey(self):
        return id(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def animate(self, tv, av, rmgr):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

