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
from TG.geomath.typeset.textblock import TextBlock
from TG.geomath.typeset.typesetter import TypeSetter
from TG.geomath.typeset.typeface import FTTypeface

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ipsum = '''\
Vestibulum tortor. Integer fermentum mi vitae augue venenatis pharetra. Pellentesque nunc. Fusce elementum. In hac habitasse platea dictumst. Fusce massa quam, gravida et, malesuada et, pellentesque nec, ante. Suspendisse risus nibh, vulputate vulputate, varius quis, elementum nec, justo. Sed vitae ipsum sed libero pharetra congue. Aenean ultrices turpis quis turpis. Morbi mattis, ipsum ut mollis suscipit, massa urna pulvinar urna, sit amet posuere eros odio ut tortor. Nulla accumsan, massa nec scelerisque bibendum, sapien nibh placerat erat, ut scelerisque magna tortor id libero. Fusce lorem justo, dapibus vel, tincidunt id, viverra sit amet, sem. Mauris pharetra sapien scelerisque arcu. Proin nec ante pretium nibh suscipit volutpat. Nunc commodo, enim eu iaculis egestas, risus magna vulputate elit, vitae euismod nibh tellus quis odio. In tincidunt. Etiam porta, pede a cursus consectetuer, est lorem dignissim dolor, in vestibulum eros sapien nec eros. Integer quis risus ut dui volutpat dignissim. Praesent vitae velit ac justo vestibulum viverra.

Morbi justo tellus, vehicula non, aliquam at, varius vel, lacus. Mauris nec magna. Pellentesque libero. Vivamus quis sem. Vestibulum et arcu eget arcu condimentum dignissim. Etiam velit dui, sodales nec, rutrum vel, sagittis at, sem. Quisque lacinia. In hac habitasse platea dictumst. Vestibulum semper, erat et molestie congue, dolor dui dapibus dolor, ut viverra elit mi in odio. Fusce elit mauris, volutpat ut, faucibus scelerisque, commodo id, eros. Etiam vulputate nibh et tellus. Nulla quis pede. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc purus tortor, vestibulum quis, ornare sed, posuere eu, arcu. Etiam lobortis elit quis nunc. Donec ornare, libero et lobortis tristique, arcu dolor convallis turpis, id hendrerit pede orci vel augue. Nam a nibh. Aliquam vel lectus.

Fusce dui odio, vulputate quis, laoreet sit amet, ullamcorper et, tellus. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Suspendisse a lectus. Duis dolor quam, ullamcorper eget, auctor ac, condimentum vel, purus. Ut augue. Donec porttitor porta erat. Nulla vel ligula. Vivamus in quam eu est vehicula pellentesque. Nulla auctor, magna in elementum rutrum, erat ante semper lacus, id porttitor lectus nibh nec nulla. Quisque tincidunt. Cras non sapien sit amet eros bibendum convallis. Nunc magna quam, pellentesque nec, suscipit non, ornare id, augue. Donec at neque.

Sed ac ipsum sit amet pede ullamcorper varius. Quisque nec odio ut eros egestas tempus. Quisque eu metus. Aliquam erat volutpat. Pellentesque tincidunt convallis magna. Donec non nunc in nunc tempor nonummy. Nam ac urna eget velit ornare dictum. Nam eu ligula. Aliquam at odio a nisl convallis aliquam. Maecenas tempus suscipit libero. Nunc sollicitudin tincidunt tortor. Mauris sem augue, egestas eu, vulputate non, pulvinar ut, mi. Maecenas posuere nisi id diam. Aliquam ac nisl non ligula congue faucibus.

Nunc et magna. Aenean vel metus. Duis in tortor. Proin commodo orci in odio. Integer nibh eros, sollicitudin nonummy, condimentum et, venenatis ut, ipsum. Proin pede purus, eleifend a, interdum feugiat, ullamcorper non, est. Curabitur laoreet est a arcu. Integer ullamcorper pede non tortor. Vivamus mollis lacinia mauris. Pellentesque a nunc pharetra nisi pretium tristique. Duis nec felis. Quisque blandit scelerisque leo. Nam fermentum elementum elit. Donec mauris risus, imperdiet non, vulputate et, malesuada ac, dolor. Integer lectus augue, posuere vel, tincidunt ac, dignissim vel, turpis. Nulla facilisi.
'''

def main():
    #fn = '/Library/Fonts/Zapfino.dfont'
    fn = '/Library/Fonts/Arial'
    face0 = FTTypeface(fn, 32)
    fn = '/System/Library/Fonts/Monaco.dfont'
    face1 = FTTypeface(fn, 48)
    faces = [face0, face1]
    colors = ['red', 'blue', 'green', 'white', ]

    if 1:
        alignModeList = ['left']
        ts = TypeSetter(wrapMode='line')
        lines = open(__file__, 'rU').readlines()
        #del lines[:-10]
        #del lines[:-2]

    else:
        alignModeList = ['left', 'center', 'right']
        alignModeList = ['center']
        ts = TypeSetter(wrapSize=1000, wrapMode='text')
        lines = [e+'\n' for e in ipsum.split('\n')]

    if 0:
        ts.block = TextBlock(True, (256, 256))
    for alignMode in alignModeList:
        ts.attr(align=alignMode)

        t0 = time.time()
        for idx, line in enumerate(lines):
            ts.write(line, face=faces[idx%2], color=colors[idx%4])
            if idx % 2 == 1:
                ts.flush()

        block = ts.compile()
        t1 = time.time()

        if 1:
            print
            print 'TypeSet Text:', alignMode
            for bl in block.lines:
                print 'p0[%5d:%5d] p1[%5d:%5d]:' % tuple(bl.box.astype('i').toflatlist()),
                print '%4d: "%-.120s"' % (len(bl.text), bl.text.encode('unicode-escape'))

        if 1:
            print
            print 'Pages used to render text:'
            for p, psl in sorted(block.pageMap.items()):
                if p is not None:
                    p = block.arena.pages.index(p)
                print 'page%-4r = text[%4d:%4d]; %d glyphs' % (p, psl.start, psl.stop, psl.stop - psl.start, )

    #block.arena.save()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    main()
