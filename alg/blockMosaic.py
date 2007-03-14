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

from bisect import insort, bisect_left, bisect_right

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

maxSentinal = object()

class LayoutException(Exception): 
    pass
class LayoutRoomException(LayoutException): 
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Block object
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Block(object):
    x = y = x1 = y1 = w = h = 0
    key = None

    def __nonzero__(self):
        return (self.w>0 and self.h>0)

    maxSentinal = maxSentinal
    def __cmp__(self, other):
        if (other is self.maxSentinal): 
            return -1
        else: 
            return cmp(self.key, other.key)

    @classmethod
    def fromSize(klass, size, key=None):
        self = klass()
        self.size = size
        if key is not None:
            self.key = key
        return self

    @classmethod
    def fromPosSize(klass, pos, size, key=None):
        self = klass()
        self.pos = pos
        self.size = size
        if key is not None:
            self.key = key
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getRect(self):
        return (self.x, self.y, self.x1, self.y1)
    def getPos(self):
        return self.x, self.y
    def setPos(self, pos):
        self.x, self.y = pos
        self._updatePos2()
    pos = property(getPos, setPos)

    def getPos1(self):
        return self.x1, self.y1
    def setPos1(self, pos):
        self.x1, self.y1 = pos
        self._updateSize()
    pos1 = property(getPos1, setPos1)

    def offset(self, pos, fromRgn=None):
        if fromRgn is not None:
            pos = tuple(l+r for l,r in zip(pos, fromRgn.pos))
        self.pos = pos

    def getSize(self):
        return self.w, self.h
    def setSize(self, size):
        self.w, self.h = size
        self._updatePos2()
    size = property(getSize, setSize)

    def getArea(self, borders=0):
        return (self.w + borders*2)*(self.h + borders*2)
    area = property(getArea)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _updateSize(self):
        self.w = self.x1 - self.x
        self.h = self.y1 - self.y
    def _updatePos2(self):
        self.x1 = self.x + self.w
        self.y1 = self.y + self.h

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Block Mosic Algorithm
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlockMosaicAlg(object):
    BlockFactory = Block
    LayoutRegionFactory = None
    borders = 1

    def __init__(self, maxSize=None):
        self._blocks = []
        if maxSize:
            self.maxSize = maxSize

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addBlock(self, size, key=None):
        block = self.BlockFactory.fromSize(size, key)
        self._blocks.append(block)
        return block

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _maxWidth = None
    def getMaxWidth(self):
        return self._maxWidth
    def setMaxWidth(self, maxWidth):
        self._maxWidth = maxWidth
    maxWidth = property(getMaxWidth, setMaxWidth)

    _maxHeight = None
    def getMaxHeight(self):
        return self._maxHeight or self.getMaxWidth()
    def setMaxHeight(self, maxHeight):
        self._maxHeight = maxHeight
    maxHeight = property(getMaxHeight, setMaxHeight)

    def getMaxSize(self):
        return (self.maxWidth, self.maxHeight)
    def setMaxSize(self, maxSize):
        if isinstance(maxSize, tuple):
            (self.maxWidth, self.maxHeight) = maxSize
        else:
            self.maxWidth, self.maxHeight = maxSize
    maxSize = property(getMaxSize, setMaxSize)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def layout(self, borders=NotImplemented):
        return self.layoutSize(self.getMaxSize(), borders)

    def layoutSize(self, size, borders=NotImplemented):
        rgn = self.LayoutRegionFactory(size)
        return self.layoutRegion(rgn, borders)

    def layoutRegion(self, rgn, borders=NotImplemented):
        if borders is NotImplemented: 
            borders = self.borders

        return rgn.layoutBlocks(self._blocks, borders)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Layout Regions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LayoutRegion(object):
    maxSentinal = maxSentinal

    RegionFactory = Block.fromPosSize
    NarrowRegionFactory = RegionFactory
    BlockRegionFactory = RegionFactory
    UnusedRegionFactory = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, size, blocks=None):
        self.setRgnFromSize(size)
        if blocks:
            self.setBlocks(blocks)

    def layoutBlocks(self, blocks, borders=1):
        self.setBlocks(blocks)
        return self.layout(borders)

    def setBlocks(self, blocks):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def layout(self, borders=1):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _rgn = None
    def getRgn(self):
        return self._rgn
    def setRgn(self, rgn):
        self._rgn = rgn
    rgn = property(getRgn, setRgn)

    def setRgnFromSize(self, size):
        self.setRgnFromPosSize((0,0), size)
    def setRgnFromPosSize(self, pos, size):
        self.rgn = self.RegionFactory(pos, size)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    minKeepDim = 10
    unused = None

    def addUnusedBlockRgn(self, pos, size, key=None):
        rgn = self.BlockRegionFactory(pos, size, key)
        return self.addUnusedRgn(rgn, True)

    def addUnusedNarrowRgn(self, pos, size, key=None):
        rgn = self.NarrowRegionFactory(pos, size, key)
        return self.addUnusedRgn(rgn, False)

    def addUnusedWasteRgn(self, pos, size, key=None):
        if self.UnusedRegionFactory is not None:
            rgn = self.UnusedRegionFactory(pos, size, key)
            return self.addUnusedRgn(rgn, None)

    def addUnusedRgn(self, rgn, rgnIsBlock):
        if min(rgn.size) < self.minKeepDim: 
            return None

        if self.unused is None:
            self.unused = []

        self.unused.append(rgn)
        return rgn

    def printUnused(self, exclude=()):
        print "Font Texture size:", self.rgn.size
        print '  Unused Regions:'
        total = 0
        for r in self.unused:
            if r.key in exclude: continue
            total += r.area
            print '    %5s <+ %5s' % (total, r.area), ':', r.key, 's:', r.size, 'p:', r.pos
        print '  -- unused :', total, 'ratio:', total/float(self.rgn.area) 

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @staticmethod
    def _avgDeltaGroups(v):
        dv = [e1-e0 for e0, e1 in zip(v[:-1], v[1:])] + [0]
        dAvg = sum(dv, 0.)/len(dv)

        p = v[0]
        r = [p]
        for n in v[1:]:
            if n-p > dAvg:
                yield r
                r = []
            r.append(n)
            p = n

        if r: yield r

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Horizontal Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HorizontalLayoutRegion(LayoutRegion):
    pass

class HorizontalRowLayoutRegion(HorizontalLayoutRegion):
    def setBlocks(self, blocks):
        self._blocks = sorted([(b.w, b) for b in blocks])

    def layout(self, borders=1):
        result = []
        rgn = self.getRgn()
        maxSentinal = self.maxSentinal
        widthMap = self._blocks

        cx = borders; cy = borders
        hMax = 0

        while widthMap:
            # Use bisect to find a block that is smaller than the remaining row width
            i = bisect_right(widthMap, (rgn.w - cx, maxSentinal)) - 1

            if i < 0: break

            # we found one, pop it off
            elemW, block = widthMap.pop(i)

            # adjust it's layout position
            block.offset((cx, cy), fromRgn=rgn)
            hMax = max(block.h, hMax)

            # and return it
            result.append(block)

            # advance horizontally
            cx += elemW + borders*2

        # mark the rest of this row as unused
        endRng = self.addUnusedNarrowRgn((cx, cy), (rgn.w-cx, hMax), key='Row')

        y = cy+hMax
        bottomRgn = self.addUnusedBlockRgn((0, y), (rgn.w, rgn.h-y), key='Bottom')

        usedSize = (rgn.w, y)
        remaining = [b[1] for b in self._blocks]
        return usedSize, result, remaining

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HorizontalBlockLayoutRegion(HorizontalLayoutRegion):
    def setBlocks(self, blocks):
        blocksByWidth = {}
        for b in blocks:
            blocksByWidth.setdefault(b.w, []).append(b)
        self._blocksByWidth = blocksByWidth

    def _avgDeltaWidths(self):
        return self._avgDeltaGroups(sorted(self._blocksByWidth.keys()))

    def layout(self, borders=1):
        rgn = self.getRgn()
        raise NotImplementedError()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Vertical Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class VerticalLayoutRegion(LayoutRegion):
    pass

class VerticalColumnLayoutRegion(VerticalLayoutRegion):
    def setBlocks(self, blocks):
        self._blocks = sorted([(b.h, b) for b in blocks])

    def layout(self, borders=1):
        result = []
        rgn = self.getRgn()
        maxSentinal = self.maxSentinal
        heightMap = self._blocks

        cx = borders; cy = borders
        wMax = 0
        while heightMap:
            # Use bisect to find a block that is smaller than the remaining row heightMap
            i = bisect_right(heightMap, (rgn.h-cy, maxSentinal)) - 1
            if i < 0: break

            # we found one, pop it off
            elemH, block = heightMap.pop(i)

            # adjust it's layout position
            block.offset((cx, cy), fromRgn=rgn)
            wMax = max(block.w, wMax)

            # and return it
            result.append(block)

            # advance vertically
            cy += elemH + borders*2

        # mark the rest of this row as unused
        endRng = self.addUnusedNarrowRgn((cx, cy), (wMax, rgn.h - cy), key='Column')

        x = cx + wMax
        bottomRgn = self.addUnusedBlockRgn((x,0), (rgn.w-x, rgn.h), key='Right')

        usedSize = (x, rgn.h)
        remaining = [b[1] for b in self._blocks]
        return usedSize, result, remaining

class VerticalBlockLayoutRegion(VerticalLayoutRegion):
    bBreakGroups = False

    def setBlocks(self, blocks):
        blocksByHeight = {}
        for b in blocks:
            blocksByHeight.setdefault(b.h, []).append((b.w, b))
        self._blocksByHeight = blocksByHeight

    def _avgDeltaHeights(self):
        return self._avgDeltaGroups(sorted(self._blocksByHeight.keys()))

    def layout(self, borders=1):
        result = []
        rgn = self.getRgn()

        heightMap = self._blocksByHeight
        heightGrps = self._avgDeltaHeights()

        maxSentinal = self.maxSentinal
        bOutOfRoom = False
        hMax = 0
        x = y = borders
        xMax = x
        for heightGrp in heightGrps:
            for elemH in heightGrp:
                widthMap = heightMap[elemH]
                if not widthMap:
                    continue

                if elemH > hMax:
                    # mark the height delta as unused
                    heightRgn = self.addUnusedWasteRgn((x, y), (x, (elemH-hMax)))
                    hMax = elemH
                elif elemH < hMax:
                    raise LayoutException("Heights are not in increasing order")

                bOutOfRoom = (y+hMax > rgn.h)
                if bOutOfRoom: break

                rowWidth = rgn.w - x
                while widthMap:
                    # Use bisect to find a block that is smaller than the remaining row width
                    i = bisect_right(widthMap, (rowWidth, maxSentinal)) - 1

                    if i >= 0:
                        # we found one, pop it off
                        elemW, block = widthMap.pop(i)

                        # adjust it's layout position
                        block.offset((x, y), fromRgn=rgn)

                        # and return it
                        result.append(block)

                        # advance horizontally
                        x += elemW + borders*2
                        xMax = max(x, xMax)
                        rowWidth = rgn.w - x

                        bNewRow = rowWidth < (elemW >> 1)
                    else:
                        # there are no blocks small enough to fit on this row
                        bNewRow = True


                    if bNewRow:
                        # mark the rest of this row as unused
                        endRng = self.addUnusedNarrowRgn((x, y), (rowWidth, hMax), key='Row')

                        # advance to the beginning of the next row
                        y += hMax + borders*2
                        hMax = elemH
                        x = borders
                        rowWidth = rgn.w - x

                        bOutOfRoom = (y+hMax > rgn.h)
                        if bOutOfRoom: break
                if bOutOfRoom: break
            if bOutOfRoom: break

            if self.bBreakGroups and (0 < rowWidth < x):
                # mark the rest of this row as unused
                endRng = self.addUnusedNarrowRgn((x, y), (rowWidth, hMax), key='Group')

                # advance to the beginning of the next row
                y += hMax + borders*2
                hMax = 0
                x = borders
                rowWidth = rgn.w - x

        if x > borders:
            lastRowRgn = self.addUnusedNarrowRgn((x, y), (rowWidth, hMax), key='Last')

        x = 0; y += hMax
        bottomRgn = self.addUnusedBlockRgn((x, y), (rgn.w - x, rgn.h - y), key='Bottom')

        usedSize = (xMax, y)
        remaining = [b[1] for wm in self._blocksByHeight.itervalues() for b in wm]
        return usedSize, result, remaining

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlockMosaicAlg.LayoutRegionFactory = VerticalBlockLayoutRegion
#BlockMosaicAlg.LayoutRegionFactory = HorizontalRowLayoutRegion
#BlockMosaicAlg.LayoutRegionFactory = VerticalColumnLayoutRegion

