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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DataProperty(object):
    missing = object()
    private = None
    public = None

    def __init__(self, data):
        self.data = data
        self.dataType = type(data)

    def onObservableClassInit(self, propertyName, obKlass):
        self.public = propertyName
        self.private = "__ob_"+propertyName
    def onObservableInit(self, propertyName, obInst):
        if self.data is not None:
            self.__get__(obInst, obInst.__class__)

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
            self.__set__(obInst, result)
            return (True, result)
    def __set__(self, obInst, value):
        if isinstance(value, self.dataType):
            setattr(obInst, self.private, value)
            self._modified_(obInst)
            return 

        item = self.__get__(obInst, None)
        item[:] = value

    def _modified_(self, obInst):
        pass

def dataProperty(klass, *args, **kw):
    data = klass(*args, **kw)
    return DataProperty(data)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Data Property
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVDataProperty(DataProperty):
    def __init__(self, data=NotImplemented, publish=None):
        if publish:
            self.public = publish
        DataProperty.__init__(self, data)

    def onObservableClassInit(self, propertyName, obKlass):
        if self.public is None:
            self.public = propertyName
        self.private = "__kv_"+propertyName

    def _modified_(self, obInst):
        obInst.kvpub(self.public, obInst)

def kvDataProperty(klass, *args, **kw):
    data = klass(*args, **kw)
    return KVDataProperty(data)

