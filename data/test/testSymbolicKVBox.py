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
from TG.geomath.data.kvBox import KVBox
import testSymbolicBox 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVBoxSymbolic(testSymbolicBox.TestBoxSymbolic):
    Box = KVBox

    def setUp(self):
        super(TestKVBoxSymbolic, self).setUp()
        self.kvoCount = 0
        self.sbox.kvpub.add('*', self.onSboxChange)

    def onSboxChange(self, sbox, key):
        self.kvoCount += 1

    def test_offset(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_offset()
        self.assertEqual(self.kvoCount, 1)

    def test_offset_2d(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_offset_2d()
        self.assertEqual(self.kvoCount, 1)

    def test_inset(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_inset()
        self.assertEqual(self.kvoCount, 1)

    def test_inset_2d(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_inset_2d()
        self.assertEqual(self.kvoCount, 1)

    def test_scaleAt(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_scaleAt()
        self.assertEqual(self.kvoCount, 1)

    def test_accessors_left_modify(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_accessors_left_modify()
        self.assertEqual(self.kvoCount, 3)

    def test_accessors_right_modify(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_accessors_right_modify()
        self.assertEqual(self.kvoCount, 3)

    def test_accessors_height_modify(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_accessors_height_modify()
        self.assertEqual(self.kvoCount, 2)

    def test_accessors_width_modify(self):
        self.assertEqual(self.kvoCount, 0)
        super(TestKVBoxSymbolic, self).test_accessors_width_modify()
        self.assertEqual(self.kvoCount, 2)

class TestKVBoxVectorSymbolic(testSymbolicBox.TestBoxVectorSymbolic):
    Box = KVBox

    def setUp(self):
        super(TestKVBoxVectorSymbolic, self).setUp()
        self.kvoCount = 0
        self.sbox.kvpub.add('*', self.onSboxChange)

    def onSboxChange(self, sbox, key):
        self.kvoCount += 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

