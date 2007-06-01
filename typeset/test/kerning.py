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

def main():
    bPrintLines = False
    bTimeWrapping = True

    #fn = '/Library/Fonts/Arial'
    fn = '/Library/Fonts/Courier New'
    face = FTTypeface(fn, 48)
    wrapSize = (1280, 960)

    text = open(__file__, 'rU').read()
    assert 'AVG' in text

    ts = TypeSetter(face = face)
    ts.add(text)

    wrapper = None
    if bPrintLines:
        print
        print 'None wrapper:'
        for w in ts.wrap(wrapSize, wrapper):
            off = w.sorts['offset']
            off = (off[-1] - off[0] + w.sorts[-1]['advance']).sum()
            print '%25r %5s: |%-.50s|' % (w, off, w.text.encode('unicode-escape'))

    if bTimeWrapping:
        print
        print 'Time None wrapper:'
        for x in xrange(5):
            ts = TypeSetter(face = face)
            t0 = time.time()
            ts.add(text)
            lines = list(ts.wrap(wrapSize, wrapper))
            t1 = time.time()
            print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), len(lines))
        print

    wrapper = "lines"
    if bPrintLines:
        print
        print 'Line wrapper:'
        for w in ts.wrap(wrapSize, wrapper):
            off = w.sorts['offset']
            off = (off[-1] - off[0] + w.sorts[-1]['advance']).sum()
            print '%25r %5s: |%-.50s|' % (w, off, w.text.encode('unicode-escape'))

    if bTimeWrapping:
        print
        print 'Time Line wrapper:'
        for x in xrange(5):
            ts = TypeSetter(face = face)
            t0 = time.time()
            ts.add(text)
            lines = list(ts.wrap(wrapSize, wrapper))
            t1 = time.time()
            print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), len(lines))
        print

    wrapper = "text"
    if bPrintLines:
        print
        print 'Text wrapper:'
        for w in ts.wrap(wrapSize, wrapper):
            off = w.sorts['offset']
            if len(off): off = (off[-1] - off[0] + w.sorts[-1]['advance']).sum()
            else: off = 0
            print '%25r %5s: |%-.50s|' % (w, off, w.text.encode('unicode-escape'))

    if bTimeWrapping:
        print
        print 'Time Text wrapper:'
        for x in xrange(5):
            ts = TypeSetter(face = face)
            t0 = time.time()
            ts.add(text)
            lines = list(ts.wrap(wrapSize, wrapper))
            t1 = time.time()
            print '%1.6fs, %.3f Mbps, %d glyphs, lines: %d' % ((t1-t0), len(text)*Mbps/(t1-t0), len(text), len(lines))
        print

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    main()
