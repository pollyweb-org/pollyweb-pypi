# 📚 STRUCT

from __future__ import annotations
from typing import Union

from .TESTS import RAWABLE
from .UTILS import UTILS


##import ruamel.yaml
##from ruamel.yaml import yaml_object
##@yaml_object(yaml)
class STRUCT_BASE(RAWABLE, object): 
    ''' 
    👉 Generic structure that wraps a non-STRUCT object. 
    If a STRUCT object is received to be wrapped, 
    it first unwraps to get the and store only the given inner object.
    
    * STRUCT({}) -> ${}
    * STRUCT(${}) -> ${}
    * STRUCT({a:1}) -> ${a:1}
    * STRUCT(None) -> $None
    '''



    def __init__(self, obj:any=None, attRoot=None):
        if isinstance(obj, STRUCT_BASE):
            # Handle a struct.
            self._obj = obj._obj
            self._attRoot = obj._attRoot
            self._attMap =  obj._attRoot
        else:
            # Handle any other object, including inheritances of struct.
            safe = STRUCT_BASE.Unstruct(obj)
            self._obj = safe
            self._attRoot = safe 
            self._attMap = {}
            if attRoot:
                self._attRoot = attRoot


    def UTILS(self):
        return UTILS()

    
    def MapAtt(self, alias:str, att:str):
        '''👉 Add alias to attributes.
        * ${a:1}.Att(b) -> None
        * ${a:1}.MapAtt(a,b).Att(b) -> 1
        * ${a:{x:2}}.MapAtt(a.x,b).Att(b) -> 2
        '''
        self._attMap[alias] = att
        return self


    @staticmethod
    def Unstruct(obj:Union[STRUCT_BASE,any]) -> any:
        ''' 👉 If the object is a STRUCT, returns the inner object. 
        * Unstruct(x) -> x
        * Unstruct($x) -> x
        * Unstruct({a:1}) -> {a:1}
        * Unstruct(${a:1}) -> {a:1}
        '''
        if isinstance(obj, STRUCT_BASE):
            return obj.Obj()
        return obj


    def Obj(self, replace=None) -> any:
        ''' 👉 Returns or replaces the inner object. 

        Getter:
        * ${a:1}.Obj() -> {a:1}
        * $None.Obj() -> None
        * ${}.Obj() -> {}

        Setter:
        * ${}.Obj({a:1}) -> {a:1}
        * ${}.Obj(${a:1}) -> {a:1}  # unwraps a struct
        * ${}.Obj(None) -> {}       # supports empty
        '''
        if replace != None:
            if isinstance(replace, STRUCT_BASE):
                self._obj = replace.Obj()
            else:
                self._obj = replace
        
        if hasattr(self, '_obj'):
            return self._obj
        else: 
            return None
    



    def __eq__(self, __value:STRUCT_BASE) -> bool:
        from .UTILS import UTILS
        
        if __value == None:
            return False
        
        elif isinstance(__value, dict):
            UTILS.AssertIsDict(self._obj)
            return self._obj == __value
        
        elif isinstance(__value, str):
            UTILS.AssertIsStr(self._obj)
            return self._obj == __value
        
        elif not isinstance(__value, STRUCT_BASE):
            if self._obj == None:
                return None == __value
            from .LOG import LOG
            LOG.RaiseException(
                f'💥 Not allowed: structs can only be compared with dicts or other structs!',
                f'Given=({type(__value)})',
                f'Value=({__value})',
                f'Self=', self)
        
        else:    
            return self._obj == __value._obj
        


    

    def Merge(self, struct:Union[any, "STRUCT_BASE"]):
        """ 👉 Merges another structure into this structure. 
        * Add object: ${a:1}.Merge({b:2}) -> ${a:1, b:2}
        * Add struct: ${a:1}.Merge(${b:2}) -> ${a:1, b:2}
        * Override : ${a:1}.Merge({b:2, a:3}) -> ${a:3, b:2}
        """
        from .STRUCT import STRUCT
        obj1:dict = self.Obj()
        obj2:dict = STRUCT(struct).Obj()
        obj1.update(obj2)
        return self


