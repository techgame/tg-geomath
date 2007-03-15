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

def doPrintTest(self, question, answer):
    strQuestion = str(question).replace('\n','')
    strAnswer = str(answer).replace('\n','')
    self.failUnlessEqual(strQuestion, strAnswer)

class TestBoxSymbolic(unittest.TestCase):
    Box = Box

    def setUp(self):
        self.boxData = numpy.array([[sym.l, sym.b], [sym.r, sym.t]])
        self.sbox = self.Box(self.boxData.copy())

    doPrintTest = doPrintTest

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
    def test_accessors_left_modify(self):
        self.sbox.x0 = sym.new_x0
        self.doPrintTest(self.sbox.x0, 'new_x0')
        self.sbox.l = sym.new_l
        self.doPrintTest(self.sbox.l, 'new_l')
        self.sbox.left = sym.new_left
        self.doPrintTest(self.sbox.left, 'new_left')

    def test_accessors_right(self):
        result = 'r'
        self.doPrintTest(self.sbox.x1, result)
        self.doPrintTest(self.sbox.r, result)
        self.doPrintTest(self.sbox.right, result)
        self.doPrintTest(self.sbox.p1[..., 0], result)
    def test_accessors_right_modify(self):
        self.sbox.x1 = sym.new_x1
        self.doPrintTest(self.sbox.x1, 'new_x1')
        self.sbox.r = sym.new_r
        self.doPrintTest(self.sbox.r, 'new_r')
        self.sbox.right = sym.new_right
        self.doPrintTest(self.sbox.right, 'new_right')

    def test_accessors_width(self):
        result = '[(r + -l)]'
        self.doPrintTest(self.sbox.w, result)
        self.doPrintTest(self.sbox.width, result)
    def test_accessors_width_modify(self):
        self.sbox.width = sym.w
        self.doPrintTest(self.sbox.xv, '[(l + w) l]')

        result_x0 = '(((l * p) + ((l + w) * (-p + 1.0))) + ((-p + 1.0) * w))'
        result_x1 = '(((l * p) + ((l + w) * (-p + 1.0))) + -(p * w))'
        self.sbox.setWidth(sym.w, sym.p)
        self.doPrintTest(self.sbox.xv, '[%s %s]' % (result_x0, result_x1))

    def test_accessors_height(self):
        result = '[(t + -b)]'
        self.doPrintTest(self.sbox.h, result)
        self.doPrintTest(self.sbox.height, result)
    def test_accessors_height_modify(self):
        self.sbox.height = sym.h
        self.doPrintTest(self.sbox.yv, '[(b + h) b]')

        result_y0 = '(((b * 0.25) + ((b + h) * 0.75)) + (0.75 * h))'
        result_y1 = '(((b * 0.25) + ((b + h) * 0.75)) + -(0.25 * h))'
        self.sbox.setHeight(sym.h, .25)
        self.doPrintTest(self.sbox.yv, '[%s %s]' % (result_y0, result_y1))

    def test_accessors_size(self):
        result = '[(r + -l) (t + -b)]'
        self.doPrintTest(self.sbox.size, result)
    
    def test_at_exact(self):
        self.doPrintTest(self.sbox.at[0], '[l b]')
        self.doPrintTest(self.sbox.at[1], '[r t]')

        self.doPrintTest(self.sbox.pv[..., 0, :], self.sbox.at[0])
        self.doPrintTest(self.sbox.pv[..., 1, :], self.sbox.at[1])

    def test_at(self):
        resultSymX = '((r * a) + (l * (-a + 1.0)))'
        resultSymY = '((t * a) + (b * (-a + 1.0)))'
        self.doPrintTest(self.sbox.at[sym.a], '[%s %s]' % (resultSymX, resultSymY))

        resultX = '((r * 0.5) + (l * 0.5))'
        resultY = '((t * 0.5) + (b * 0.5))'
        self.doPrintTest(self.sbox.at[.5], '[%s %s]' % (resultX, resultY))

        resultX = '((r * 0.25) + (l * 0.75))'
        resultY = '((t * 0.25) + (b * 0.75))'
        self.doPrintTest(self.sbox.at[.25], '[%s %s]' % (resultX, resultY))

    def test_at_exact_size(self):
        result = '[(r + -l) (t + -b)]'
        self.doPrintTest(self.sbox.at[:], result)
        self.doPrintTest(self.sbox.at[0:], result)
        self.doPrintTest(self.sbox.at[0:1], result)
        self.doPrintTest(self.sbox.at[:1], result)

    def test_at_size(self):
        resultSymX = '((r + -l) * (s1 - s0))'
        resultSymY = '((t + -b) * (s1 - s0))'
        self.doPrintTest(self.sbox.at[sym.s0:sym.s1], '[%s %s]' % (resultSymX, resultSymY))
    
    def test_offset(self):
        result = '[[(l + d) (b + d)] [(r + d) (t + d)]]'
        self.sbox.offset(sym.d)
        self.doPrintTest(self.sbox, result)

    def test_offset_2d(self):
        result = '[[(l + dx) (b + dy)] [(r + dx) (t + dy)]]'
        self.sbox.offset((sym.dx, sym.dy))
        self.doPrintTest(self.sbox, result)

    def test_inset(self):
        result = '[[(l + d) (b + d)] [(r + -d) (t + -d)]]'
        self.sbox.inset(sym.d)
        self.doPrintTest(self.sbox, result)

    def test_inset_2d(self):
        result = '[[(l + dx) (b + dy)] [(r + -dx) (t + -dy)]]'
        self.sbox.inset((sym.dx, sym.dy))
        self.doPrintTest(self.sbox, result)
    
    def test_scaleAt(self):
        resultLeft = '(((r * p) + (l * (-p + 1.0))) + ((-p + 1.0) * ((r + -l) * s)))'
        self.sbox.scaleAt(sym.s, sym.p) 
        self.doPrintTest(self.sbox.left, resultLeft)

        resultRight = '(((r * p) + (l * (-p + 1.0))) + -(p * ((r + -l) * s)))'
        self.doPrintTest(self.sbox.right, resultRight)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestBoxSymbolicBlend(unittest.TestCase):
    Box = Box

    doPrintTest = doPrintTest

    def testBlend1d(self):
        bv = self.Box([
                [[sym.l0], [sym.r0]],
                [[sym.l1], [sym.r1]]
                ], dtype='object')
        b0 = bv[0]; b1 = bv[1]

        result_l = '[((l1 * a) + (l0 * (-a + 1.0)))]'
        result_r = '[((r1 * a) + (r0 * (-a + 1.0)))]'
        self.doPrintTest(b0.blend(sym.a, b1), '[%s %s]' % (result_l, result_r))

        self.doPrintTest(b0.blend(.25, b1), bv.blendAt[.25])

    def testBlend2d(self):
        bv = self.Box([
                [[sym.l0, sym.b0], [sym.r0, sym.t0]],
                [[sym.l1, sym.b1], [sym.r1, sym.t1]]
                ], dtype='object')
        b0 = bv[0]; b1 = bv[1]

        result_l = '[((l1 * a) + (l0 * (-a + 1.0))) ((b1 * a) + (b0 * (-a + 1.0)))]'
        result_r = '[((r1 * a) + (r0 * (-a + 1.0))) ((t1 * a) + (t0 * (-a + 1.0)))]'
        self.doPrintTest(b0.blend(sym.a, b1), '[%s %s]' % (result_l, result_r))

        self.doPrintTest(b0.blend(.25, b1), bv.blendAt[.25])

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

    doPrintTest = doPrintTest

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

    def test_accessors_width(self):
        result = '[[(r + -l)] [(r1 + -l1)]]'
        self.doPrintTest(self.sbox.w, result)
        self.doPrintTest(self.sbox.width, result)
    def test_accessors_height(self):
        result = '[[(t + -b)] [(t1 + -b1)]]'
        self.doPrintTest(self.sbox.h, result)
        self.doPrintTest(self.sbox.height, result)
    def test_accessors_size(self):
        result = '[[(r + -l) (t + -b)] [(r1 + -l1) (t1 + -b1)]]'
        self.doPrintTest(self.sbox.size, result)

    def test_at_exact(self):
        self.doPrintTest(self.sbox.at[0], '[[l b] [l1 b1]]')
        self.doPrintTest(self.sbox.at[1], '[[r t] [r1 t1]]')

        self.doPrintTest(self.sbox.pv[..., 0, :], self.sbox.at[0])
        self.doPrintTest(self.sbox.pv[..., 1, :], self.sbox.at[1])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

