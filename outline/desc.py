# -*- coding: UTF-8 -*-
'''
@desc : 数据描述符
'''
from .libs import md5
from random import uniform
class Desc():
    pass

class ConstDesc(Desc):
    def __init__(self,default=None):
        self._value   = default
        self._writeable = True
        super().__init__()
    def __set__(self,instance,value):
        assert self._writeable ,EOFError("attempt to recover const data description")
        self._value = value

    def __get__(self,instance,owner):
        return self._value

class VariableDesc(Desc):
    def __init__(self,default=None):
        self._value = default
        super().__init__()
    def __set__(self,instance,value):
        self._value = value
    def __get__(self,instance,owner):
        return self._value
class LetDesc(Desc):
    def __init__(self,default=None,name=None):
        self._default = default
        self.name = name if name else self.set_unk_name()
        super().__init__()
    @property
    def k(self):
        name = f"{self.__class__.__name__}_{self.name}" 
        return md5(name)
    def set_unk_name(self):
        ukn = md5(uniform(0,1)) 
        name = f"{ukn}_unk"
        return  name
    def __set__(self,instance,value):
        instance.__dict__[self.k] = value
    def __get__(self,instance,owner):
        resp = instance.__dict__.get(self.k,None)
        if resp is None:
            instance.__dict__[self.k] = self._default
            resp = self._default
        return resp





