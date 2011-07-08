##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GraphPassBase(object):
    depthFirst = True
    skipRoot = False
    nextLevelFor = 'children'
    levelStrategies = {
        'children': (lambda cnode: cnode.children),
        +1: (lambda cnode: cnode.children),

        'parents': (lambda cnode: cnode.parents),
        -1: (lambda cnode: cnode.parents),
        }

    def iterNodeStack(self, root, depthFirst=None, nextLevelFor=None, skipRoot=None):
        if depthFirst is None:
            depthFirst = self.depthFirst
        if nextLevelFor is None:
            nextLevelFor = self.nextLevelFor
        if skipRoot is None:
            skipRoot = self.skipRoot

        nextLevelFor = self.levelStrategies.get(nextLevelFor, nextLevelFor)
        if skipRoot:
            nextLevel = nextLevelFor(root)
        else: nextLevel = [root]

        stack = [(None, iter(nextLevel))]

        while stack:
            if depthFirst:
                idx = len(stack) -1
            else: idx = 0
            ttree = stack[idx][1]

            for cnode in ttree:
                if cnode is None:
                    continue

                nextLevel = nextLevelFor(cnode)
                if nextLevel:
                    if (yield +1, cnode):
                        yield 'cull'
                    else:
                        stack.append((cnode, iter(nextLevel)))
                        if depthFirst: break
                else: 
                    if (yield 0, cnode):
                        yield 'noop'

            else:
                cnode = stack.pop(idx)[0]
                if cnode is not None:
                    if (yield -1, cnode):
                        yield 'noop'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GraphPass(GraphPassBase):
    def __init__(self, root):
        self.root = root

    def iter(self, depthFirst=None, nextLevelFor=None, skipRoot=None):
        return (cnode for op, cnode in 
                    self.iterNodeStack(self.root, depthFirst, nextLevelFor, skipRoot)
                        if op >= 0)
    __iter__ = iter 

    def iterStack(self, depthFirst=None, nextLevelFor=None, skipRoot=None):
        return self.iterNodeStack(self.root, depthFirst, nextLevelFor, skipRoot)

