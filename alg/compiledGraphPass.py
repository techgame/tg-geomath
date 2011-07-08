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

from functools import partial
from .graphPass import GraphPass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Compiled Graph Pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RawCompileStack(object):
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

            compileNodeTo(op, cnode, self)

            if self._cull:
                itree.send(True)
                op = 0
                self._cull = False

            step(op, cnode)

        del self._cull
        del self._unwind
        del self._stack
        return self._result_(self._result)

    def _result_(self, result):
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

class CallStackInfoMixin(object):
    def __init__(self, key, root):
        self._initInfo(key, root)

    def _initInfo(self, key, root):
        self.key = key
        self.root = root

    def __repr__(self):
        return "<%s.%s key:%r |result|:%s>" % (
            self.__class__.__module__, self.__class__.__name__, 
            self.key, len(self._result))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompileStack(RawCompileStack):
    def add(self, *items):
        self._result.extend(items)
    def addUnwind(self, *items):
        self._unwind.extend(items)
    def cull(self, bCull=True):
        self._cull = bCull

    def depth(self):
        return len(self._stack)
    def __len__(self):
        return len(self._result)
    def __iter__(self):
        return iter(self._result)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompileCallStack(CompileStack):
    def addFn(self, fn, *args):
        if args:
            fn = partial(fn, *args)
        self.add(fn)
    def addUnwindFn(self, fn, *args):
        if args:
            fn = partial(fn, *args)
        self.addUnwind(fn)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Compiled Graph Pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompiledGraphPass(GraphPass):
    class CompileCallStack(CallStackInfoMixin, CompileCallStack):
        pass

    def newCompileStack(self, key, root):
        return self.CompileCallStack(key, root)

    def compile(self, key, root=None):
        if root is None:
            root = self.root

        result = self._getCached(key, root)
        if result is not None:
            return result

        ctree = self.newCompileStack(key, root)
        itree = self.iterNodeStack(root)
        result = ctree._compile_(itree, self.compileNodeTo)

        self._setCached(key, root, result)
        return result

    def compileNodeTo(self, op, cnode, ctree):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def _getCached(self, key, root):
        return getattr(self, key, None)
    def _setCached(self, key, root, result):
        setattr(self, key, result)

