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

from operator import attrgetter
from .graphPass import GraphPass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NodeChangePass(GraphPass):
    depthFirst = False
    nextLevelFor = 'parents'

    def perform(self, changeStack=None):
        visited = set()
        changeStack = changeStack or []

        itree = self.iterStack()
        for op, node in itree:
            if op < 0: 
                changeStack.pop()
                continue
            elif node in visited:
                itree.send(True)
                continue

            visited.add(node)
            onTreeChange = node.onTreeChange
            if onTreeChange is not None:
                if onTreeChange(node, changeStack):
                    continue

            if op > 0:
                changeStack.append(node)
    __call__ = perform


class GraphNode(object):
    order = 0

    parents = None
    children = None
    
    def __init__(self, **kw):
        for n,v in kw.items():
            setattr(self, n, v)

        self.parents = []
        self.children = []

    def __del__(self):
        self.clear()
        assert not self.parents

    @classmethod
    def new(klass, **kw):
        return klass(**kw)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Node coersion
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isNode(self, nodeKlass=None): 
        if nodeKlass is not None: 
            return isinstance(self, nodeKlass)
        else: return True

    @classmethod
    def itemAsNode(klass, item, create=True):
        """Override to provide conversion and creation utilities"""
        if item.isNode(klass):
            return item

        node = None 
        if node is None and create:
            raise ValueError("Expected a Node, but received %r" % (item.__class__,))

        return node

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Graph Change Recording
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    onTreeChange = None #onTreeChange(node, changeStack)
    def treeChanged(self, changeStack=None):
        NodeChangePass(self).perform(changeStack)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Parents collection
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onAddToParent(self, parent):
        if parent not in self.parents:
            self.parents.append(parent)
        return True
        
    def onRemoveFromParent(self, parent):
        while parent in self.parents:
            self.parents.remove(parent)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Children collection
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, idx):
        return self.children[idx]
    def __setitem__(self, idx, value):
        if isinstance(idx, slice):
            if idx.step is not None:
                raise NotImplementedError("Step is not implemented for setitem")

            del self[idx]
            self.extendAt(idx.start or 0,  value)
        else: 
            self.removeAt(idx)
            self.insert(idx, value)

    def __delitem__(self, idx):
        nodeList = self.children[idx]
        del self.children[idx]
        self._removeNodeList(nodeList)

    def clear(self):
        del self[:]

    def __contains__(self, other):
        node = self.itemAsNode(other, False)
        return node in self.children

    def sort(self, key=attrgetter('order')):
        self.children.sort(key=key)

    def __iadd__(self, other):
        self.add(other)
        return self
    def __isub__(self, other):
        self.remove(other)
        return self

    def insertNew(self, idx):
        return self.insert(idx, self.new())
    def insert(self, idx, item):
        node = self.itemAsNode(item)
        if node.onAddToParent(self):
            self.children.insert(idx, node)
            self.treeChanged([node])
            return node

    def insertBefore(self, item, nidx):
        """Inserts item before index of nidx in children"""
        nidx = self.itemAsNode(nidx, False)
        idx = self.children.index(nidx)
        return self.insert(idx, item)
    def insertAfter(self, item, nidx):
        """Inserts item after index of nidx in children"""
        nidx = self.itemAsNode(nidx, False)
        idx = self.children.index(nidx) + 1
        return self.insert(idx, item)

    def newParent(self):
        parentNode = self.new()
        parentNode.add(self)
        return parentNode

    def addNew(self):
        return self.add(self.new())
    def add(self, item):
        if isinstance(item, list):
            return self.extend(item)

        node = self.itemAsNode(item)
        if node.onAddToParent(self):
            self.children.append(node)
            self.treeChanged([node])
            return node
    append = add

    def assign(self, item):
        self.clear()
        return self.add(item)

    def extend(self, iterable):
        itemAsNode = self.itemAsNode
        children = self.children

        nodeChanges = set()
        for each in iterable:
            node = itemAsNode(each)
            if node.onAddToParent(self):
                children.append(node)
                nodeChanges.add(node)
        self.treeChanged([nodeChanges])
    def extendAt(self, idx, iterable):
        itemAsNode = self.itemAsNode
        newChildren = []

        nodeChanges = set()
        for each in iterable:
            node = itemAsNode(each)
            if node.onAddToParent(self):
                newChildren.append(node)
                nodeChanges.add(node)
        self.children[idx:idx] = newChildren
        self.treeChanged([nodeChanges])

    def remove(self, item):
        if isinstance(item, list):
            return [self.remove(each) for each in item]
        node = self.itemAsNode(item, False)
        if node is None: 
            return
        if node.onRemoveFromParent(self):
            self.children.remove(node)
            self.treeChanged([node])
            return node
    def removeAt(self, idx):
        node = self.children[idx]
        if node.onRemoveFromParent(self):
            del self.children[idx]
            self.treeChanged([node])
            return node

    def _removeNodeList(self, nodeList):
        if not isinstance(nodeList, list):
            nodeList = [nodeList]
        nodeChanges = set()
        for node in nodeList:
            if node.onRemoveFromParent(self):
                nodeChanges.add(node)
        self.treeChanged([nodeChanges])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Tree debugging and printing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def printTree(self, indent=0, indentStr='  ', nextLevelFor='children'):
        print
        title = "Node Tree for: %r" % (self,)
        print title
        print "=" * len(title)

        for op, node in self.iterStack(True, nextLevelFor): 
            if op >= 0:
                print '%s- %r' % (indent*indentStr, node)
            indent += op

        print
        print

    def printParentTree(self, indent=0, indentStr='  '):
        return self.printTree(indent, indentStr, 'parents')

