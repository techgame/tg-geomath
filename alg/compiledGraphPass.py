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

class CompileStack(object):
    def add(self, *items):
        self._result.extend(items)
    def addUnwind(self, *items):
        self._unwind.extend(items)
    def cull(self, bCull=True):
        self._cull = bCull

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __len__(self):
        return len(self._result)
    def __iter__(self):
        return iter(self._result)

    def _compile_(self, itree, compileNodeTo):
        self._cull = False
        self._result = []
        self._unwind = []
        self._stack = []

        pop = self._pop_
        step = self._step_
        for op, cnode in itree:
            if op < 0:
                pop(op, cnode)
                continue

            compileNodeTo(cnode, self)

            if self._cull:
                itree.send(True)
                op = 0
                self._cull = False

            step(op, cnode)

        del self._cull
        del self._unwind
        del self._stack
        return self

    def _pop_(self, op, cnode):
        self._result.extend(self._unwind)
        self._result.extend(self._stack.pop())
        del self._unwind[:]

    def _step_(self, op, cnode):
        if op > 0:
            self._stack.append(self._unwind)
            self._unwind = []

        else:
            self._result.extend(self._unwind)
            del self._unwind[:]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompiledGraphPass(GraphPass):
    def newCompileStack(self, key, root):
        return CompileStack()

    def compile(self, key, root=None):
        if root is None:
            root = self.root

        result = self._getCached(key, root)
        if result is not None:
            return result

        ct = self.newCompileStack(key, root)
        itree = self.iterNodeStack(root)
        result = ct._compile_(itree, self.compileNodeTo)

        self._setCached(key, root, result)
        return result

    def compileNodeTo(self, cnode, ct):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def _getCached(self, key, root):
        return getattr(self, key, None), None
    def _setCached(self, key, root, result):
        setattr(self, key, result)

