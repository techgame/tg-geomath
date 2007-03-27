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

import re

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Text Wrapping
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicTextWrapper(object):
    def iterWrapText(self, wrapSize, text, textOffsets):
        for textSlice in self.wrapSlices(wrapSize, text, textOffsets):
            yield text[textSlice]

    def iterWrapSlices(self, wrapSize, text, textOffsets):
        return self.iterAvailTextSlices(wrapSize, text, textOffsets)

    def iterAvailTextSlices(self, wrapSize, text, textOffsets):
        if text: 
            yield slice(0, len(text))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RETextWrapper(BasicTextWrapper):
    re_wrapPoints = re.compile('$|\n|\r')

    def iterAvailTextSlices(self, wrapSize, text, textOffsets):
        if not text: return

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

    wrapAxis = 0
    def iterWrapSlices(self, wrapSize, text, textOffsets):
        wrapAxis = self.wrapAxis
        axisWrapSize = wrapSize[wrapAxis]
        if axisWrapSize <= 0: return

        if not text: return

        lineWraps = self.lineWraps

        iLine = 0; offLine = textOffsets[iLine, 0, wrapAxis]
        iCurr = iLine; offCurr = offLine
        for textSlice in self.iterAvailTextSlices(wrapSize, text, textOffsets):
            iNext = textSlice.stop
            offNext = textOffsets[iNext, 0, wrapAxis]

            # check to see if the next wrap slice falls off the end
            if (axisWrapSize < (offNext - offLine)):
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
    'basic': BasicTextWrapper(),
    'line': LineTextWrapper(),
    'text': TextWrapper(),
    }

