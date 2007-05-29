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
import numpy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MosaicPage(object):
    _sizeToTexCoords = numpy.array([
            [0,1],
            [1,1],
            [1,0],
            [0,0]], 'l')

    def __init__(self, pageSize):
        w, h = pageSize
        self.page = numpy.zeros((h, w), 'B')
        
        self.waste = []
        self.blocks = {}
        self._allocBlock = self._iterAllocBlocks(pageSize).send
        self._allocBlock(None)

    def _iterAllocBlocks(self, (w, h)):
        pos = numpy.array([0, 0], 'H')
        size = numpy.array([w, 0], 'H')
        th = h

        h = yield
        while 1:
            th -= h
            if th < 0: break

            size[1] = h
            h = yield (pos.copy(), size.copy())
            pos[1] += size[1]

    #_blockBins = [8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024, 2048]
    #_blockBins = [8, 16, 24, 32, 48, 64, 80, 96, 128, 192, 256, 384, 512, 1024, 2048]
    #_blockBins = sorted([e for sw in range(3, 11) for e in [1<<sw] if e < 2048])
    #_blockBins = sorted([e for sw in range(3, 11) for e in [1<<sw, 3<<sw] if e < 2048])
    _blockBins = sorted([e for sw in range(3, 11) for e in [1<<sw, 3<<sw, 5<<sw] if e < 2048])

    def findBlock(self, size, binIdx, create=True):
        bins = self._blockBins
        if create:
            binIdxEnd = binIdx+1
        else: binIdxEnd = None

        for height in bins[binIdx:binIdxEnd]:
            blocks = self.blocks.get(height)
            if blocks:
                for idx, (bpos, bsize) in enumerate(blocks):
                    if (bsize-1 > size).all():
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
        binIdx = bisect_right(self._blockBins, size[1]+1)
        idx, blocks = self.findBlock(size, binIdx, self._allocBlock is not None)
        if idx is None:
            return None

        bpos, bsize = blocks[idx]
        r = bpos.copy()
        w = size[0] + 1
        bpos[0] += w
        bsize[0] -= w
        if 3*bsize[0] < bsize[1]:
            blocks.pop(idx)

        self.waste.append(w*(bsize[1] - size[1] - 1))
        return r

    def newEntryFor(self, sort):
        bmp = sort['typeface'].bitmapFor(sort)
        if bmp is None:
            w = h = bx = by= 0
        else:
            h, w = bmp.shape
            block = self.blockFor((w, h))
            if block is None:
                return None
            bx, by = block
            self.page[by:by+h, bx:bx+w] = bmp

        coords = ((w,h) * self._sizeToTexCoords) + (bx, by)
        return self, coords

    def dataAt(self, coords):
        ((x0,y0), (x1, y1)) = coords[[3, 1]]
        return self.page[y0:y1, x0:x1]

    def imageAt(self, coords, filename=None):
        data = self.dataAt(coords)
        return self.asImage(data, filename)

    def asImage(self, data=None, filename=None):
        import PIL.Image
        if data is None:
            data = self.page

        img = PIL.Image.fromstring('L', data.shape[::-1], data.ravel())
        if filename: 
            img.save(filename)
        return img


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MosaicPageArena(object):
    def __init__(self, pageSize=(1024,1024)):
        self._entries = {}
        self.pages = []
        self.pageSize = pageSize

    def __getitem__(self, sorts):
        return map(self.getPageFor, sorts)

    def getPageFor(self, sort):
        sortkey = int(sort['hidx'])
        entry = self._entries.get(sortkey, None)
        if entry is None:
            entry = self.newEntryFor(sort)
            self._entries[sortkey] = entry
        return entry

    def newEntryFor(self, sort):
        for page in self.pages:
            entry = page.newEntryFor(sort)
            if entry is not None:
                return entry
        else:
            page = self.newPage()
            entry = page.newEntryFor(sort)
            return entry

    def newPage(self):
        r = MosaicPage(self.pageSize)
        self.pages.append(r)
        return r

