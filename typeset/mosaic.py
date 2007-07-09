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

from bisect import bisect_right
from collections import defaultdict

import numpy

from TG.metaObserving import OBFactoryMap
from TG.geomath.data import DataHostObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

defaultPageSize = (1024, 1024)
class MosaicPage(DataHostObject):
    _fm_ = OBFactoryMap(pageSize=defaultPageSize)
    entryCount = 0
    _sizeToTexCoords = numpy.array([[0.,1.], [1.,1.], [1.,0.], [0.,0.]], 'f')

    def __init__(self, pageSize=None):
        w, h = pageSize or self._fm_.pageSize
        self.data = numpy.zeros((h, w), 'B')
        
        self.blocks = {}
        self._blockBins = [(e - self.deltaSize) for e in self._blockBins if e < w]

        # initialize the generator
        self._allocBlock = self._iterAllocBlocks().send
        self._allocBlock(None)

    def getSize(self):
        h, w = self.data.shape
        return (w, h)
    size = property(getSize)

    deltaSize = 2
    def _iterAllocBlocks(self):
        deltaSize = self.deltaSize

        cw = self.size[0]
        pos = numpy.array([1, 0], 'h')
        size = numpy.array([cw, 0], 'h')
        self.allocInfo = pos, size

        h = yield
        pos[1] = deltaSize // 2
        size[1] = h
        while pos[1]+size[1] < self.data.shape[0]:
            h = yield (pos.copy(), size.copy())
            pos[1] += size[1] + deltaSize # old size + deltaSize
            size[1] = h

    _blockBins = sorted([e for sw in range(10) for e in [0x8<<sw, 0xc<<sw]])

    def findBlock(self, size, binIdx, create=True):
        bins = self._blockBins
        if create:
            binIdxEnd = binIdx+1
        else: binIdxEnd = None

        for height in bins[binIdx:binIdxEnd]:
            blocks = self.blocks.get(height)
            if blocks:
                for idx, (bpos, bsize) in enumerate(blocks):
                    if (bsize > size).all():
                        return idx, blocks

        if not create:
            return None, []

        height = bins[binIdx]
        try:
            newBlock = self._allocBlock(height)
        except StopIteration:
            self._allocBlock = None

            return self.findBlock(size, binIdx+1, False)
        else:
            blocks = self.blocks.setdefault(height, [])
            blocks.append(newBlock)
            return len(blocks)-1, blocks

    def blockFor(self, size):
        binIdx = bisect_right(self._blockBins, size[1])
        idx, blocks = self.findBlock(size, binIdx, self._allocBlock is not None)
        if idx is None:
            return None

        bpos, bsize = blocks[idx]
        r = bpos.copy()
        w = size[0] + self.deltaSize
        bpos[0] += w
        bsize[0] -= w
        if 3*bsize[0] < bsize[1]:
            blocks.pop(idx)
        return r

    def newEntryFor(self, bmp):
        h, w = bmp.shape
        block = self.blockFor((w, h))
        if block is None:
            return None
        bx, by = block

        self.data[by:by+h, bx:bx+w] = bmp
        self.entryCount += 1

        coords = ((w,h) * self._sizeToTexCoords) + (bx, by)
        return self, coords

    def dataAt(self, coords):
        ((x0,y0), (x1, y1)) = coords[[3, 1]]
        return self.data[y0:y1, x0:x1]

    def imageAt(self, coords, filename=None):
        data = self.dataAt(coords)
        return self.asImage(data, filename)

    def asImage(self, data=None, filename=None):
        import PIL.Image
        if data is None:
            data = self.data

        img = PIL.Image.fromstring('L', data.shape[::-1], data.ravel())
        if filename: 
            img.save(filename)
        return img

    def save(self, filename='page.png'):
        return self.asImage(self.data, filename)

    def printBlockInfo(self):
        print '=========================='
        width = self.size[0]/100.0
        print 'height: filled % per block'
        print '--------------------------'
        for k, v in sorted(self.blocks.items()):
            print '  %4d: [%s]' % (k, ', '.join('%1.0f%%' % (s[0]/width) for p,s in v))
        print '=========================='

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MosaicPageArena(DataHostObject):
    _fm_ = OBFactoryMap(
            Page=MosaicPage, 
            pageSize=defaultPageSize,
            )

    def __init__(self, pageSize=None):
        self._entries = {}
        self.pages = []
        self.pageSize = pageSize or self._fm_.pageSize

    def __contains__(self, sort):
        return self.pageForSort(sort, False)
    def __getitem__(self, sorts):
        return map(self.pageForSort, sorts)

    def save(self, filenames='page-%s.png'):
        for i, page in enumerate(self.pages):
            page.save(filenames % (i,))

    def texCoords(self, sorts, texCoords=None):
        pageMap = defaultdict(list)
        if texCoords is None:
            texCoords = numpy.empty((len(sorts), 4, 2), 'f')

        pageForSort = self.pageForSort
        for i, srt in enumerate(sorts):
            page, tc = pageForSort(srt) or (None, 0)
            pageMap[page].append(i)
            texCoords[i] = tc

        return pageMap, texCoords

    def texMap(self, sorts, texCoords=None):
        pageMap, texCoords = self.texCoords(sorts, texCoords)

        pimNone = pageMap.pop(None, None)
        pageMapItems = pageMap.items()
        count = sum(len(pim) for page, pim in pageMapItems)
        if pimNone: count += 1

        mapIdxPush = numpy.empty(len(sorts), 'h')
        mapIdxPull = numpy.empty(count, 'h')
        
        # All None page entries take position zero
        i0 = i1 = 0
        if pimNone is not None:
            i1 = 1
            pageMap[None] = slice(i0, i1)
            mapIdxPush[pimNone] = i0
            mapIdxPull[i0:i1] = pimNone[:i1-i0]
            i0 = i1

        for page, pim in pageMapItems:
            i1 = i0 + len(pim)
            pageMap[page] = slice(i0, i1)
            mapIdxPush[pim] = range(i0, i1)
            mapIdxPull[i0:i1] = pim
            i0 = i1

        return pageMap, mapIdxPush, mapIdxPull, texCoords

    def pageForSort(self, sort, create=True):
        sortkey = int(sort['hidx'])
        entry = self._entries.get(sortkey, None)
        if entry is None and create:
            bmp = self.sortBitmap(sort)
            entry = self.newEntryFor(bmp)
            self._entries[sortkey] = entry
        return entry

    def sortBitmap(self, sort):
        bmp = sort['typeface'].bitmapFor(sort)
        return bmp

    def newEntryFor(self, bmp):
        if bmp is None:
            return None

        for page in self.pages:
            entry = page.newEntryFor(bmp)
            if entry is not None:
                return entry

        page = self.newPageForBitmap(bmp)
        entry = page.newEntryFor(bmp)
        if entry is None:
            raise RuntimeError("No room for bmp in new page")
        return entry

    def newPageForBitmap(self, bmp):
        bh, bw = bmp.shape

        pw, ph = self.pageSize
        if bw >= pw-2 or bh >= ph-2:
            raise ValueError("Bitmap shape is bigger than mosaic page size")

        page = self.newPage((pw, ph))
        return page

    def newPage(self, pageSize=None):
        if pageSize is None:
            pageSize = self.pageSize

        r = self._fm_.Page(pageSize)
        self.pages.append(r)
        return r

