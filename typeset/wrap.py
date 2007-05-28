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
    def wrapSlices(self, size, text, offset):
        return self.wrapPoints(size, text, offset)
    def wrapPoints(self, size, text, offset):
        return [slice(0, len(text))]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RETextWrapper(BasicTextWrapper):
    re_wrapPoints = re.compile('$|\n|\r')

    def wrapPoints(self, size, text, offset):
        iterMatches = self.re_wrapPoints.finditer(text)
        i0 = 0
        for match in iterMatches:
            i1 = match.end()
            yield slice(i0, i1)
            i0 = i1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LineTextWrapper(RETextWrapper):
    re_wrapPoints = re.compile('$|\n|\r')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextWrapper(RETextWrapper):
    lineWraps = '\n\r'
    re_wrapPoints = re.compile('[\s-]|$')

    def wrapSlices(self, size, text, offset):
        wrapAxis = offset[-1].argmax()
        wrapSize = size[wrapAxis]
        offset = offset[..., wrapAxis]

        lineWraps = self.lineWraps

        iLine = 0; offLine = offset[iLine]
        iCurr = iLine; offCurr = offLine
        for textSlice in self.wrapPoints(size, text, offset):
            iNext = textSlice.stop
            if iNext >= len(offset):
                break

            offNext = offset[iNext]

            # check to see if the next wrap slice falls off the end
            if (wrapSize < (offNext - offLine)):
                yield slice(iLine, iCurr)
                iLine = iCurr; offLine = offCurr

            # check to see if we have a linewrap at the current position
            if text[iNext-1] in lineWraps:
                yield slice(iLine, iNext)
                iLine = iNext; offLine = offNext

            iCurr = iNext; offCurr = offNext

        iNext = len(text)
        if iLine < iNext:
            yield slice(iLine, iNext)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Wrap Mode Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wrapModeMap = {
    'none': BasicTextWrapper,
    'line': LineTextWrapper,
    'text': TextWrapper,
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

