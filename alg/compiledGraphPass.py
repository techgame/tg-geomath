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

from .graphPass import GraphPass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Compiled Graph Pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CallTree(object):
    def add(self, *fns):
        self._wind.extend(fns)
    def addUnwind(self, *fns):
        self._unwind.extend(fns)
    def cull(self, bCull=True):
        self._cull = bCull

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _compile_(self, itree, compileNodeTo):
        self._wind = []
        self._unwind = []
        self._stack = []

        performOp = self._op_
        for op, node in itree:
            self._cull = False
            performOp(op, node, itree, compileNodeTo)

        assert not self._unwind, ('Unwind list not empty:', self._unwind)
        assert not self._stack, ('Unwind stack not empty:', self._stack)
        return self._wind

    def _op_(self, op, node, itree, compileNodeTo):
        if op < 0:
            self._wind.extend(self._unwind)
            self._wind.extend(self._stack.pop())
            del self._unwind[:]
            return

        compileNodeTo(node, self)

        if op == 0 or self._cull:
            self._wind.extend(self._unwind)
            del self._unwind[:]

            if op > 0: 
                itree.send(True)

        else: # op > 0
            self._stack.append(self._unwind)
            self._unwind = []

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompiledGraphPass(GraphPass):
    singlePass = False

    def __init__(self, node, singlePass=False):
        self.node = node
        node.onTreeChange = self._node_onTreeRootChange
        if singlePass is not self.singlePass:
            self.singlePass = singlePass

    def _node_onTreeRootChange(self, rootNode, cause=None):
        self._cachePassList(None)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newCallTree(self):
        return CallTree()

    def compile(self):
        result = self._cachePassList()
        if result is not None:
            return result

        ct = self.newCallTree()
        result = ct._compile_(self.iterStack(), self.compileNodeTo)
        self._cachePassList(result)
        return result

    _passList = None
    def _cachePassList(self, passList=NotImplemented):
        if passList is not NotImplemented:
            if passList is None:
                self._passList = None
            elif self.singlePass:
                self._passList = []
            else:
                self._passList = passList 
        return self._passList

    def compileNodeTo(self, node, ct):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

