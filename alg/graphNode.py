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

import weakref
from operator import attrgetter
from .graphPass import GraphPass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NodeChangePass(GraphPass):
    depthFirst = False
    nextLevelFor = 'parents'

    def perform(self, cause=None):
        visited = set()
        itree = self.iterStack()
        for op, node in itree:
            if op < 0: 
                continue
            elif node in visited:
                itree.send(True)
                continue
            elif node.treeChangeSuspend:
                node.treeChangeSuspend += 1
                visited.add(node)
                itree.send(True)
                continue

            visited.add(node)
            onTreeChange = node.onTreeChange
            if onTreeChange is not None:
                if onTreeChange(node, cause):
                    itree.send(True)
                    continue
    __call__ = perform


class GraphNode(object):
    order = 0

    def __init__(self):
        self._parents = []
        self._children = []

    @classmethod
    def new(klass):
        return klass()

    def asWeakRef(self, cb=None, ref=weakref.ref):
        return ref(self, cb)
    def asWeakProxy(self, cb=None, proxy=weakref.proxy):
        return proxy(self, cb)

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

    def iter(self):
        return GraphPass(self).iter()
    def iterParents(self):
        return GraphPass(self).iter(nextLevelFor='parents')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Graph Change Recording
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    onTreeChange = None #onTreeChange(node, cause)
    treeChangeSuspend = False
    def treeChanged(self, cause=None):
        if self.treeChangeSuspend:
            self.treeChangeSuspend += 1
            return

        NodeChangePass(self).perform(cause)

    def __enter__(self):
        self.treeChangeSuspend = True
        return self

    def __exit__(self, exc=None, exctype=None, tb=None):
        tcs = self.treeChangeSuspend 
        del self.treeChangeSuspend
        if tcs > True:
            self.treeChanged()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Parents collection
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _parents = None
    def getParents(self):
        return [p() for p in self._parents if p() is not None]
    parents = property(getParents)

    def onAddToParent(self, parent):
        collection = self._parents
        parent = parent.asWeakRef()
        if parent not in collection:
            collection.append(parent)
        return True
        
    def onRemoveFromParent(self, parent):
        collection = self._parents
        parent = parent.asWeakRef()
        if parent in collection:
            collection.remove(parent)
        return True

    def disconnect(self):
        for p in self.parents:
            p.remove(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Children collection
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _children = None
    def getChildren(self):
        return self._children
    children = property(getChildren)
    
    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return iter(self._children)

    def __getitem__(self, idx):
        return self._children[idx]
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
        nodeList = self._children[idx]
        del self._children[idx]
        self._removeNodeList(nodeList)

    def clear(self):
        del self[:]

    def __contains__(self, other):
        node = self.itemAsNode(other, False)
        return node in self._children

    def sort(self, key=attrgetter('order')):
        self._children.sort(key=key)

    def __iadd__(self, other):
        self.add(other)
        return self
    def __isub__(self, other):
        self.remove(other)
        return self

    def insertNew(self, idx=0):
        return self.insert(idx, self.new())
    def insert(self, idx, item):
        node = self.itemAsNode(item)
        if node.onAddToParent(self):
            self._children.insert(idx, node)
            self.treeChanged(node)
            return node

    def insertBefore(self, item, nidx):
        """Inserts item before index of nidx in _children"""
        nidx = self.itemAsNode(nidx, False)
        idx = self._children.index(nidx)
        return self.insert(idx, item)
    def insertAfter(self, item, nidx):
        """Inserts item after index of nidx in _children"""
        nidx = self.itemAsNode(nidx, False)
        idx = self._children.index(nidx) + 1
        return self.insert(idx, item)

    def newParent(self):
        parentNode = self.new()
        parentNode.add(self)
        return parentNode

    def addNew(self):
        return self.add(self.new())
    appendNew = addNew

    def add(self, item):
        if isinstance(item, list):
            return self.extend(item)

        node = self.itemAsNode(item)
        if node.onAddToParent(self):
            self._children.append(node)
            self.treeChanged(node)
            return node
    append = add

    def assign(self, item):
        self.clear()
        if item is not None:
            return self.add(item)

    def extend(self, iterable):
        itemAsNode = self.itemAsNode
        _children = self._children

        nodeChanges = set()
        for each in iterable:
            node = itemAsNode(each)
            if node.onAddToParent(self):
                _children.append(node)
                nodeChanges.add(node)

        if nodeChanges:
            self.treeChanged(nodeChanges)
    def extendAt(self, idx, iterable):
        itemAsNode = self.itemAsNode
        newChildren = []

        nodeChanges = set()
        for each in iterable:
            node = itemAsNode(each)
            if node.onAddToParent(self):
                newChildren.append(node)
                nodeChanges.add(node)

        if nodeChanges:
            self._children[idx:idx] = newChildren
            self.treeChanged(nodeChanges)

    def remove(self, item):
        if isinstance(item, list):
            return [self.remove(each) for each in item]
        node = self.itemAsNode(item, False)
        if node is None: 
            return
        if node.onRemoveFromParent(self):
            self._children.remove(node)
            self.treeChanged(node)
            return node
    def removeAt(self, idx):
        node = self._children[idx]
        if node.onRemoveFromParent(self):
            del self._children[idx]
            self.treeChanged(node)
            return node

    def _removeNodeList(self, nodeList):
        if not isinstance(nodeList, list):
            nodeList = [nodeList]

        nodeChanges = set()
        for node in nodeList:
            if node.onRemoveFromParent(self):
                nodeChanges.add(node)

        if nodeChanges:
            self.treeChanged(nodeChanges)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Tree debugging and printing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def printTree(self, nextLevelFor='children', indent=0, indentStr='  ', title="Node Tree for: %r", fout=None):
        title = title % (self,)
        print >> fout, title
        print >> fout, "=" * len(title)

        itree = GraphPass(self).iterStack(True, nextLevelFor)
        for op, node in itree:
            if op >= 0:
                print >> fout, '%s- %r' % (indent*indentStr, node)
            indent += op

    def printParentTree(self, nextLevelFor='parents', indent=0, indentStr='  ', fout=None, ):
        return self.printTree(nextLevelFor, indent, indentStr, fout)

