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

import unittest
import numpy
from TG.geomath.data.box import Box
from TG.geomath.data.symbolic import sym, evalExpr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestBoxSymbolic(unittest.TestCase):
    Box = Box

    def setUp(self):
        self.boxData = numpy.array([[sym.l, sym.b], [sym.r, sym.t]])
        self.sbox = self.Box(self.boxData.copy())

    def doPrintTest(self, question, reprAnswer):
        reprQuestion = str(question).replace('\n','')
        self.failUnlessEqual(reprQuestion, reprAnswer)

    def test_box(self):
        result = '[[l b] [r t]]'
        self.doPrintTest(self.sbox, result)
        self.doPrintTest(self.sbox.pv, result)

    def test_accessors_p0(self):
        result = '[l b]'
        self.doPrintTest(self.sbox.pos, result)
        self.doPrintTest(self.sbox.p0, result)
        self.doPrintTest(self.sbox.pv[..., 0, :], result)
    def test_accessors_p1(self):
        result = '[r t]'
        self.doPrintTest(self.sbox.corner, result)
        self.doPrintTest(self.sbox.p1, result)
        self.doPrintTest(self.sbox.pv[..., 1, :], result)

    def test_accessors_left(self):
        result = 'l'
        self.doPrintTest(self.sbox.x0, result)
        self.doPrintTest(self.sbox.l, result)
        self.doPrintTest(self.sbox.left, result)
        self.doPrintTest(self.sbox.p0[..., 0], result)
    def test_accessors_right(self):
        result = 'r'
        self.doPrintTest(self.sbox.x1, result)
        self.doPrintTest(self.sbox.r, result)
        self.doPrintTest(self.sbox.right, result)
        self.doPrintTest(self.sbox.p1[..., 0], result)

    def test_accessor_width(self):
        result = '[(r + -l)]'
        self.doPrintTest(self.sbox.w, result)
        self.doPrintTest(self.sbox.width, result)
    def test_accessor_height(self):
        result = '[(t + -b)]'
        self.doPrintTest(self.sbox.h, result)
        self.doPrintTest(self.sbox.height, result)
    def test_accessor_size(self):
        result = '[(r + -l) (t + -b)]'
        self.doPrintTest(self.sbox.size, result)

        #print
        #print boxn.atPos(sym.a)
        #print box.atPos((sym.xa, sym.ya))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Vector version of the test
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestBoxVectorSymbolic(unittest.TestCase):
    Box = Box

    def setUp(self):
        self.boxData = numpy.array([
            [[sym.l, sym.b], [sym.r, sym.t]],
            [[sym.l1, sym.b1], [sym.r1, sym.t1]]])

        self.sbox = self.Box(self.boxData.copy())

    def doPrintTest(self, question, reprAnswer):
        reprQuestion = str(question).replace('\n','')
        self.failUnlessEqual(reprQuestion, reprAnswer)

    def test_box(self):
        result = '[[[l b]  [r t]] [[l1 b1]  [r1 t1]]]'
        self.doPrintTest(self.sbox, result)
        self.doPrintTest(self.sbox.pv, result)

        result0 = '[[l b] [r t]]'
        self.doPrintTest(self.sbox[0], result0)
        self.doPrintTest(self.sbox[0].pv, result0)

        result1 = '[[l1 b1] [r1 t1]]'
        self.doPrintTest(self.sbox[1], result1)
        self.doPrintTest(self.sbox[1].pv, result1)

    def test_accessors_p0(self):
        result = '[[l b] [l1 b1]]'
        self.doPrintTest(self.sbox.pos, result)
        self.doPrintTest(self.sbox.p0, result)
        self.doPrintTest(self.sbox.pv[..., 0, :], result)
    def test_accessors_p1(self):
        result = '[[r t] [r1 t1]]'
        self.doPrintTest(self.sbox.corner, result)
        self.doPrintTest(self.sbox.p1, result)
        self.doPrintTest(self.sbox.pv[..., 1, :], result)

    def test_accessors_left(self):
        result = '[l l1]'
        self.doPrintTest(self.sbox.x0, result)
        self.doPrintTest(self.sbox.l, result)
        self.doPrintTest(self.sbox.left, result)
        self.doPrintTest(self.sbox.p0[..., 0], result)
    def test_accessors_right(self):
        result = '[r r1]'
        self.doPrintTest(self.sbox.x1, result)
        self.doPrintTest(self.sbox.r, result)
        self.doPrintTest(self.sbox.right, result)
        self.doPrintTest(self.sbox.p1[..., 0], result)

    def test_accessor_width(self):
        result = '[[(r + -l)] [(r1 + -l1)]]'
        self.doPrintTest(self.sbox.w, result)
        self.doPrintTest(self.sbox.width, result)
    def test_accessor_height(self):
        result = '[[(t + -b)] [(t1 + -b1)]]'
        self.doPrintTest(self.sbox.h, result)
        self.doPrintTest(self.sbox.height, result)
    def test_accessor_size(self):
        result = '[[(r + -l) (t + -b)] [(r1 + -l1) (t1 + -b1)]]'
        self.doPrintTest(self.sbox.size, result)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

