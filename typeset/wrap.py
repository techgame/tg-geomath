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

import re
from numpy import asarray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Text Wrapping
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicTextWrapper(object):
    def wrapSlices(self, size, textRange, text, offset):
        if len(offset):
            return self.wrapPoints(size, textRange, text, offset)
        else: return []
    def wrapPoints(self, size, textRange, text, offset):
        return [textRange]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RETextWrapper(BasicTextWrapper):
    re_wrapPoints = re.compile('$', re.MULTILINE)

    def wrapPoints(self, size, textRange, text, offset):
        i0 = textRange.start; i1 = textRange.stop
        iterMatches = self.re_wrapPoints.finditer(text, i0, i1)
        for match in iterMatches:
            i1 = match.end() + 1
            if i1-i0 <= 1 and i1>len(text):
                break

            yield slice(i0, i1)
            i0 = i1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LineTextWrapper(RETextWrapper):
    re_wrapPoints = re.compile('$', re.MULTILINE)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextWrapper(RETextWrapper):
    lineWraps = '\n\r'
    re_wrapPoints = re.compile('[\s-]|$')#, re.MULTILINE)

    def wrapSlices(self, size, textRange, text, offset):
        if not len(offset):
            return

        wrapAxis = offset[-1].argmax()
        wrapSize = size[wrapAxis]
        offset = offset[..., wrapAxis]

        lineWraps = self.lineWraps

        iLine = textRange.start; offLine = offset[iLine]
        iCurr = iLine; offCurr = offLine
        for textSlice in self.wrapPoints(size, textRange, text, offset):
            iNext = textSlice.stop-1
            if iNext < len(offset):
                offNext = offset[iNext]
            else: offNext = offset[-1]

            # check to see if the next wrap slice falls off the end
            if (wrapSize < (offNext - offLine)):
                yield slice(iLine, iCurr)
                iLine = iCurr; offLine = offCurr

            # check to see if we have a linewrap at the current position
            if text[iNext-1] in lineWraps:
                if iLine < iNext:
                    yield slice(iLine, iNext)
                iLine = iNext; offLine = offNext

            iCurr = iNext; offCurr = offNext

        iNext = textRange.stop
        if iLine < iNext:
            yield slice(iLine, iNext)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Wrap Mode Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wrapModeMap = {
    'none': BasicTextWrapper(),
    'line': LineTextWrapper(),
    'text': TextWrapper(),
    }
wrapModeMap[None] = wrapModeMap['none']
wrapModeMap['basic'] = wrapModeMap['none']

wrapModeMap[False] = wrapModeMap['line']
wrapModeMap['false'] = wrapModeMap['line']
wrapModeMap['lines'] = wrapModeMap['line']
wrapModeMap['normal'] = wrapModeMap['line']

wrapModeMap[True] = wrapModeMap['text']
wrapModeMap['true'] = wrapModeMap['text']
wrapModeMap['paragraph'] = wrapModeMap['text']
wrapModeMap['wrap'] = wrapModeMap['text']

