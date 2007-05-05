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
    def on(self, fn):
        self.add(fn)
        return fn
    def add(self, *fns):
        self._wind.extend(fns)

    def onUnwind(self, fn):
        self.addUnwind(fn)
        return fn
    def addUnwind(self, *fns):
        self._unwind.extend(fns)

    def cull(self, bCull=True):
        self._cull = bCull

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompiledGraphPass(GraphPass):
    singlePass = False

    def __init__(self, node, singlePass=False):
        self.node = node
        node.onTreeChange = self._node_onTreeRootChange
        if singlePass is not self.singlePass:
            self.singlePass = singlePass

    def _node_onTreeRootChange(self, rootNode, treeChanges=None):
        self._cachePassList(None)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newCallTree(self):
        return CallTree()

    def compile(self):
        result = self._cachePassList()
        if result is not None:
            return result

        compileNodeTo = self.compileNodeTo
        ct = self.newCallTree()
        ct._wind = []; ct._unwind = []; ct._stack = []

        itree = self.iterStack()
        for op, node in itree:
            ct._cull = False

            if op < 0:
                ct._wind.extend(ct._unwind)
                ct._wind.extend(ct._stack.pop())
                del ct._unwind[:]
                continue

            compileNodeTo(node, ct)

            if op == 0 or ct._cull:
                ct._wind.extend(ct._unwind)
                del ct._unwind[:]

                if op > 0: itree.send(True)

            else: # op > 0
                ct._stack.append(ct._unwind)
                ct._unwind = []

        result = ct._wind
        assert not ct._unwind, ('Unwind list not empty:', self._unwind)
        assert not ct._stack, ('Unwind stack not empty:', self._stack)

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

