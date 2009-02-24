#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import numpy

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pMat = numpy.array(
       [[ 0,  2,  0,  0],
        [-1,  0,  1,  0],
        [ 2, -5,  4, -1],
        [-1,  3, -3,  1]], numpy.double)

def vtMat(t, pMat=pMat):
    t = numpy.asarray(t)
    vt = numpy.array([t, t, t, t], 'double')

    vt[0] = 1.
    vt[2] *= vt[1]
    vt[3] *= vt[2]
    vt *= 0.5
    vt = vt.T

    vtMat = numpy.dot(vt, pMat)
    return vtMat

def p(t, av, pMat=pMat):
    vm = vtMat(t, pMat)
    return numpy.dot(vm, av)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    n = 10
    if 0: e = 1e-15
    else: e = 0
    t = numpy.arange(0., 1.+e, 1./n)

    avData = [0, 0, 1, 0, 2, 0, 1, 0, 4, 0, 2, 0, 8, 0, 0]
    avRes = None
    for i in xrange(0, len(avData)-3):
        av = avData[i:i+4]
        avp = p(t, av)
        if avRes is not None:
            avRes = numpy.concatenate([avRes, avp], 0)
        else: avRes = avp

        r = numpy.vstack([t, avp]).T
        r[:,0] += i
        for e in r:
            print '%f,%f' % tuple(e)
