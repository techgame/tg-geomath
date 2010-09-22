#!/usr/bin/env python
# -*- coding: utf-8 -*-
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from collections import defaultdict

import numpy
from numpy import array, asmatrix, identity, outer, cos, sin, radians

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MatrixStack(object):
    def __init__(self, key=None):
        self.initMatrixStacks(key)

    def initMatrixStacks(self, key=None):
        self._matStacks = defaultdict(self._newStack)
        self.changeStack(key)

    def _newStack(self):
        return [asmatrix(identity(4))]
    def changeStack(self, key):
        self._matCurrent = self._matStacks[key]

    @property
    def top(self):
        return self._matCurrent[-1]
    @top.setter
    def top(self, m):
        self._matCurrent[-1] = asmatrix(m)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def push(self):
        MC = self._matCurrent
        MC.append(MC[-1].copy())
        return self
    def pop(self):
        self._matCurrent.pop()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def ortho(self, x0, x1, y0, y1, z0, z1):
        w = (x1-x0); tx = (x1+x0)/w;
        h = (y1-y0); ty = (y1+y0)/h;
        d = (z1-z0); tz = (z1+z0)/d;

        m = asmatrix(
           [[2./w,   0.,    0., -tx],
            [  0., 2./h,    0., -ty],
            [  0.,   0., -2./d, -tz],
            [  0.,   0.,    0.,  1.]], 'd')

        self.top *= m
        return self

    def identity(self):
        self.top = identity(4)
        return self

    def scale(self, sx=1., sy=1., sz=1.):
        m = identity(4)
        m *= [sx,sy,sz,1.]
        self.top *= m
        return self

    def translate(self, tx=0., ty=0., tz=0.):
        m = identity(4)
        m[:,3] = [tx,ty,tz,1.]
        self.top *= m
        return self

    def rotate(self, a=0., vx=0., vy=0., vz=1.):
        a = radians(a)
        u = array([vx,vy,vz,0], 'd')

        uut = outer(u,u)
        M = identity(4)-uut
        S = array([[ 0., -vz,  vy, 0.],
                   [ vz,  0., -vx, 0.],
                   [-vy,  vx,  0., 0.],
                   [ 0.,  0.,  0., 1.]], 'd')

        R = uut + numpy.cos(a)*M + numpy.sin(a)*S
        R[3,3] = 1.
        self.top *= R
        return self

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    ms = MatrixStack()
    print
    print "Around Z axis"
    print ms.identity().rotate(30).top.round(3)
    print ms.identity().rotate(45).top.round(3)
    print ms.identity().rotate(60).top.round(3)
    print ms.identity().rotate(90).top.round(3)

    print
    print "Around Y axis"
    print ms.identity().rotate(30, 0, 1, 0).top.round(3)
    print ms.identity().rotate(45, 0, 1, 0).top.round(3)
    print ms.identity().rotate(60, 0, 1, 0).top.round(3)
    print ms.identity().rotate(90, 0, 1, 0).top.round(3)

    print
    print "Around X axis"
    print ms.identity().rotate(30, 1, 0, 0).top.round(3)
    print ms.identity().rotate(45, 1, 0, 0).top.round(3)
    print ms.identity().rotate(60, 1, 0, 0).top.round(3)
    print ms.identity().rotate(90, 1, 0, 0).top.round(3)

