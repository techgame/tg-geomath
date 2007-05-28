#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from TG.metaObserving import MetaObservalbeObject
from TG.geomath.data.color import Color
from TG.geomath.data.box import Box
from TG.geomath.animate.targets import TargetView, animateAt

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Actor(MetaObservalbeObject):
    color = Color.property('#ff', dtype='B')
    box = Box.property([-1,-1], [1, 1], dtype='b')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    a = Actor()

    v1 = Color('#00')

    ao = TargetView(a)
    ao.color[:] = v1

    print 
    tm = 8
    for ti in xrange(tm+1):
        t = float(ti)/tm
        animateAt(t)
        print '%.5f: %s' % (t, a.color.hex)

    print 
    ao.box[:] = Box([10,10], [20,20])
    for ti in xrange(tm//2+1):
        t = float(ti)/tm
        animateAt(t)
        print '%.5f: %s' % (t, a.box.toflatlist())

    print 
    ao.box[:] = Box([100,0], [110,10])
    for ti in xrange(tm+1):
        t = float(ti)/tm
        animateAt(t)
        print '%.5f: %s' % (t, a.box.toflatlist())

