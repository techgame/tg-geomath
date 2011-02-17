#!/usr/bin/env python
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

import numpy
from numpy import ndarray, array, vander, dot

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Bezier(ndarray):
    __array_priority__ = -1

    order = {}

    def __new__(klass, groupKey, *args, **kw):
        self = groups[groupKey]
        if args or kw:
            return self(*args, **kw)
        else:
            return self

    def at(self, pts, u):
        if isinstance(pts, list):
            pts = numpy.asarray(pts)
        Bp = dot(self, pts)
        uM = vander(u, len(self))
        return dot(uM, Bp)
    __call__ = at

    def atP(self, pts):
        if isinstance(pts, list):
            pts = numpy.asarray(pts)
        Bp = dot(self, pts)
        Bp = Bp.view(BezierP)
        return Bp
    dot = atP

    def atU(self, u):
        uM = vander(u, len(self))
        uB = dot(uM, self)
        return uB.view(UBezier)

class UBezier(ndarray):
    __array_priority__ = -1

    def atP(self, pts):
        if isinstance(pts, list):
            pts = numpy.asarray(pts)
        return dot(self, pts)
    __call__ = at = atP
    dot = atP
    __mul__ = dot

class BezierP(ndarray):
    __array_priority__ = -1

    def atU(self, u):
        try: uM = vander(u, len(self))
        except TypeError:
            uM = vander([u], len(self))
        return dot(uM, self)
    __call__ = at = atU

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

for Mb in [
        array([[-1,  1], [ 1,  0]], 'b'),
        array([[ 1, -2,  1], [-2,  2,  0], [ 1,  0,  0]], 'b'),
        array([[-1,  3, -3,  1], [ 3, -6,  3,  0], [-3,  3,  0,  0], [ 1,  0,  0,  0]], 'b'),
        ]:
    Bezier.order[len(Mb)-1] = Mb.view(Bezier)

b1 = bLinear = Bezier.linear = Bezier.order[1]
b2 = bQuadratic = Bezier.quadratic = Bezier.order[2]
b3 = bCubic = Bezier.cubic = Bezier.order[3]

groups = {
    'a0': bCubic.atP([0., 1., 0., 1.]),
    '~a0': bCubic.atP([1., 0., 1., 0.]),

    'a': bCubic.atP([0., 0.5, 0.5, 1.]),
    '~a': bCubic.atP([1., 0.5, 0.5, 0.]),
    'a1': bCubic.atP([0., 0.5, 0.5, 1.]),
    '~a1': bCubic.atP([1., 0.5, 0.5, 0.]),

    'a2': bCubic.atP([0., 0.25, 0.75, 1.]),
    '~a2': bCubic.atP([1., 0.75, 0.25, 0.]),

    'a3': bCubic.atP([0., 0.125, 0.875, 1.]),
    '~a3': bCubic.atP([1., 0.875, 0.125, 0.]),

    'a4': bCubic.atP([0., 0.0625, 0.9375, 1.]),
    '~a4': bCubic.atP([1., 0.9375, 0.0625, 0.]),

    'ak': bCubic.atP([0., 0., 1., 1.]),
    '~ak': bCubic.atP([1., 1., 0., 0.]),

    'fast': bCubic.atP([0., 1., 1., 1.]),
    '~fast': bCubic.atP([1., 0., 0., 0.]),

    'slow': bCubic.atP([0., 0., 0., 1.]),
    '~slow': bCubic.atP([1., 1., 1., 0.]),
    }


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    from TG.geomath.data.color import colorVector
    cpts = colorVector(['#000', '#70f', '#f48', '#fff'])
    u = [0., .25, .5, .75, 1.]

    print
    if 1:
        print 'B1:'
        print b1.at([cpts[0], cpts[3]], u).astype('B')
        print 

    if 1:
        print
        print 'B2:'
        print b2.atP([cpts[0], cpts[2], cpts[3]]).atU(u).astype('B')
        print

    if 1:
        print
        print 'B3:'
        print (b3.atU(u)*cpts).astype('B')
        print

    if 1:
        print
        print 'B3 blend:'
        print Bezier('ak')
        bu = Bezier('ak', u)
        r = b1.atU(bu)*[cpts[0], cpts[3]]
        print r
        print


