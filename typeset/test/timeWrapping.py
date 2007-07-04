#!/usr/bin/env python
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

import sys, time
from TG.geomath.typeset.typesetter import TypeSetter
from TG.geomath.typeset.typeface import FTTypeface

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mbps = 1./(1<<17)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextBlock(object):
    def __init__(self, text, sorts, slice):
        self.text = text
        self.sorts = sorts
        self.slice = slice

    def __repr__(self):
        return '<%s [%04s:%04s]>' % (self.__class__.__name__, self.slice.start, self.slice.stop)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    bPrintLines = False
    bTimeWrapping = True

    fn = '/Library/Fonts/Zapfino.dfont'
    face = FTTypeface(fn, 48)
    wrapSize = (1280, 960)

    text = open(__file__, 'rU').read()
    if bPrintLines:
        ts = TypeSetter(face = face)
        ts.write(text)

    elif bTimeWrapping:
        face.translate(text)

    wrapper = None
    if bPrintLines:
        print
        print 'None wrapper:'
        for ws in ts.wrapSlices(wrapSize, wrapper):
            wsorts = ts.sorts[ws]; wtext = ts.text[ws]
            off = wsorts['offset']
            off = (off[-1] - off[0] + wsorts[-1]['advance']).sum()
            print '%25r %5s: |%-.50s|' % (w, off, wtext.encode('unicode-escape'))

    if bTimeWrapping:
        print
        print 'Time None wrapper:'
        for x in xrange(5):
            ts = TypeSetter(face = face)
            t0 = time.time()
            ts.write(text)
            lines = list(ts.wrapSlices(wrapSize, wrapper))
            t1 = time.time()
            print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), len(lines))
        print

    wrapper = "lines"
    if bPrintLines:
        print
        print 'Line wrapper:'
        for ws in ts.wrapSlices(wrapSize, wrapper):
            wsorts = ts.sorts[ws]; wtext = ts.text[ws]
            off = wsorts['offset']
            off = (off[-1] - off[0] + wsorts[-1]['advance']).sum()
            print '%25r %5s: |%-.50s|' % (w, off, wtext.encode('unicode-escape'))

    if bTimeWrapping:
        print
        print 'Time Line wrapper:'
        for x in xrange(5):
            ts = TypeSetter(face = face)
            t0 = time.time()
            ts.write(text)
            lines = list(ts.wrapSlices(wrapSize, wrapper))
            t1 = time.time()
            print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), len(lines))
        print

    wrapper = "text"
    if bPrintLines:
        print
        print 'Text wrapper:'
        for ws in ts.wrapSlices(wrapSize, wrapper):
            wsorts = ts.sorts[ws]; wtext = ts.text[ws]
            off = wsorts['offset']
            if len(off): off = (off[-1] - off[0] + wsorts[-1]['advance']).sum()
            else: off = 0
            print '%25r %5s: |%-.50s|' % (w, off, wtext.encode('unicode-escape'))

    if bTimeWrapping:
        print
        print 'Time Text wrapper:'
        for x in xrange(5):
            ts = TypeSetter(face = face)
            t0 = time.time()
            ts.write(text)
            lines = list(ts.wrapSlices(wrapSize, wrapper))
            t1 = time.time()
            print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), len(lines))
        print

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    main()
