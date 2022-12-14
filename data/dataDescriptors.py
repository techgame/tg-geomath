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

from . import DataHostObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DataProperty(object):
    missing = object()
    public = None
    private = None
    _private_fmt = '__ob_%s'

    def __init__(self, data, publish=None):
        self._setPublishName(publish)
        self.data = data

    def _setPublishName(self, publish):
        if publish is None or isinstance(self.public, str):
            return

        self.public = publish
        self.private = self._private_fmt % (publish,)

    def propertyNameTuple(self):
        return (self.public, self.private)

    def onObservableClassInit(self, propertyName, obKlass):
        self._setPublishName(propertyName)

    def __get__(self, obInst, obKlass):
        if obInst is None:
            return self
        missing = self.missing
        result = getattr(obInst, self.private, missing)
        if result is missing:
            factoryResult = self.setWithFactory(obInst)
            if not factoryResult:
                raise AttributeError("'%s' object attribute '%s' has not been initialized" % (obInst, self.public))
            else: result = factoryResult[-1]
        return result

    def setWithFactory(self, obInst):
        data = self.data
        if data is not None:
            result = data.copy()
            self.__set_factory__(obInst, result)
            return (True, result)
    def set(self, obInst, value):
        setattr(obInst, self.private, value)
        self._modified_(obInst)

    def __set__(self, obInst, value):
        if isinstance(value, self.data.__class__):
            return self.set(obInst, value) 

        item = self.__get__(obInst, None)
        itemSetValue = getattr(item, '__setvalue__', None)
        if itemSetValue is not None:
            itemSetValue(value)
        else: item[:] = value
    __set_factory__ = set

    def _modified_(self, obInst):
        pass

def dataProperty(klass, *args, **kw):
    publish = kw.pop('publish', None)
    data = klass(*args, **kw)
    return DataProperty(data, publish)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Data Property
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVDataProperty(DataProperty):
    _private_fmt = '__kv_%s'

    def _modified_(self, obInst):
        obInst.kvpub.publishProp(self.public, obInst)

def kvDataProperty(klass, *args, **kw):
    publish = kw.pop('publish', None)
    data = klass(*args, **kw)
    return KVDataProperty(data, publish)

