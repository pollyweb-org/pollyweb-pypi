# 📚 STRUCT

from __future__ import annotations
from typing import Union
from datetime import datetime

from .LOG import LOG
from .UTILS import UTILS
from .LOG import LOG

from .STRUCT_BASE import STRUCT_BASE

class STRUCT_ATTRIBUTES(STRUCT_BASE): 
    


    def IsMissingOrEmpty(self, name:str=None) -> bool:
        """ 
        👉 Indicates if the object or an attribute is missing or empty. 

        Returns True when:
        * ${}.IsMissingOrEmpty() -> True
        * $None.IsMissingOrEmpty() -> True
        * ${a:None}.IsMissingOrEmpty('a') -> True
        * ${a:{}}.IsMissingOrEmpty('a') -> True
        * ${a:''}.IsMissingOrEmpty('a') -> True
        * ${a:'  '}.IsMissingOrEmpty('a') -> True
        
        Returns False when:
        * ${a:False}.IsMissingOrEmpty('a') -> False
        * ${False}.IsMissingOrEmpty() -> False
        * ${a:None}.IsMissingOrEmpty() -> False
        * ${a:1}.IsMissingOrEmpty('a') -> False
        * ${a:'y'}.IsMissingOrEmpty('a') -> False
        * ${a:{b:2}}.IsMissingOrEmpty('a') -> False
        """
        ##LOG.Print(f'STRUCT.IsMissingOrEmpty(name={name})')

        # the root
        if name == None:
            return self._obj == None or self._obj == {}
        
        # the attribute
        val = self.GetAtt(name)
        if val == None or val == {} or str(val).strip() == '':
            
            ##LOG.Print(f'>>> True @STRUCT.IsMissingOrEmpty(name={name})')
            return True
        
        ##LOG.Print(f'>>> False @STRUCT.IsMissingOrEmpty(name={name}): val={val}')
        return False




    def SetAttRoot(self, attRoot:str, noHierarchy:bool=True):
        ''' 
        👉 Sets the root for the Att() method. 
        Useful for an envelope where the attributes are in the body.
        * ${a:x,b:{y:2}}.SetAttRoot(b).Att(y) -> 2 (searchs root)
        * ${a:x,b:{y:2}}.SetAttRoot(b).Att(a) -> x (also searchs all)
        * ${}.SetAttRoot(x) -> Exception! (require att to exist)
        * ${x}.SetAttRoot(None) -> Exception! (requires att name)
        ''' 
        UTILS.RequireArgs([attRoot])
        root = self.RequireAtt(attRoot, noHierarchy=noHierarchy)
        self._attRoot = root
        return self



    

    def __getitem__(self, att:str):
        ''' 👉 Same as RequireAtt(name).
        * ${A:1}.Att('A') -> 1
        * ${A:1}['A'] -> 1
        '''
        ##LOG.Print(f'STRUCT.__getitem__(att={att})')

        UTILS.RequireArgs(att)
        
        # Read indexes in a loop like: if 'ID' in STRUCT({ID:1})
        if isinstance(att, int):
            
            attName = self.Attributes()[att]
            UTILS.AssertIsType(attName, str)
            
            ##LOG.Print(f'  STRUCT.__getitem__({att}) -> {attName}')
            return attName

        # Otherwise, read attribute names.
        if not isinstance(att,str):
            LOG.RaiseValidationException(f'Only str indexes are implemented, received att={type(att).__name__}:{att} on {self._obj}')
        
        ##LOG.Print(f'  STRUCT.__getitem__(att={att}): calling self.Att(att, noHierarchy=True)')
        if not self.ContainsAtt(att):
            LOG.RaiseValidationException(
                f'Att [{att}] not found in [{self.Obj()}]!')

        return self.GetAtt(
            name=att, 
            noHierarchy=True)


    def __setitem__(self, att:str, set:any):
        ''' 👉 Same as SetAtt(name).
        * ${A:1}.SetAtt('A',1) 
        * ${A:1}['A'] = 1
        '''
        UTILS.RequireArgs(att)
        
        if not isinstance(att,str):
            LOG.RaiseValidationException(f'Only str indexes are implemented, found: {att}')
        
        return self.SetAtt(name=att, set=set)
    


    def MoveAtt(self, att:str, new_position:int) -> STRUCT_BASE:
        ''' 👉 Moves an item to a different position.
        * ${A:1,B:2}.MoveAtt(B,0) -> {B:2,A1}
        '''
        odict:dict = self._obj
        odict[att] = odict.pop(att)
        i = 0
        items = UTILS.Copy(odict).items()
        for key, value in items:
            if key != att and i >= new_position:
                odict[key] = odict.pop(key)
            i += 1

        return self
    

    def ContainsAtt(self, att:str) -> bool:
        ''' 👉 Indicates if an attribute exists in the internal object.
        * ${a:1}.ContainsAtt(a) -> True
        * ${a:1}.ContainsAtt(b) -> False
        * ${}.ContainsAtt(b) -> False
        ''' 
        
        if self.IsMissingOrEmpty():
            return False
        
        obj = self.Obj()
        if type(obj) in [str,int,float,bool]:
            return False

        return att in self.Obj()
    

    def AssertOnlyKeys(self, keys:list[str], context=None):
        ''' 👉 Throws an exception if the object has keys other than the ones provided.
        * ${}.AssertOnlyKeys([]) -> OK
        * ${a:1,b:2}.AssertOnlyKeys([a,b]) -> OK
        * ${a:1,b:2}.AssertOnlyKeys([a]) -> Exception!
        * ${a:1,b:2}.AssertOnlyKeys([a,c]) -> Exception!
        '''
        UTILS.AssertIsList(keys, itemType=str)

        for key in self.Attributes():
            if key not in keys:
                LOG.RaiseValidationException(
                    f'Invalid key [{key}] found', 
                    f'Expected= {keys}', 
                    self, context)
                
        return self


    def SortedKeys(self) -> list[str]:
        ''' 👉 Returns the keys of the internal object sorted. 
        * ${b:2, a:1}.SortedKeys() -> [a,b]
        '''
        UTILS.AssertIsDict(self)
        return sorted(self.Attributes())


    def Keys(self) -> list[str]:
        ''' 👉 Returns the keys of the internal object. 
        * Same as Attributes()
        * ${a:1, b:2}.Keys() -> [a,b]
        '''
        return self.Attributes()
    

    def IsStr(self, att:str=None) -> bool:
        ''' 👉 Indicates if the object or an attribute is a string. 
        * ${a:'x'}.IsStr(a) -> True
        * ${a:1}.IsStr(a) -> False
        * ${a:None}.IsStr(a) -> False
        * ${}.IsStr() -> False
        * $None.IsStr() -> False
        '''
        if att == None:
            return isinstance(self.Obj(), str)
        return isinstance(self.GetAtt(att), str)


    def IsList(self, att:str=None) -> bool:
        ''' 👉 Indicates if the object or an attribute is a list. 
        * ${a:[1,2]}.IsList(a) -> True
        * ${a:1}.IsList(a) -> False
        * ${a:None}.IsList(a) -> False
        * ${}.IsList() -> False
        * $None.IsList() -> False
        '''
        if att == None:
            return isinstance(self.Obj(), list)
        return isinstance(self.GetAtt(att), list)


    def IsClass(self, cls:type, att:str=None) -> bool:
        ''' 👉 Indicates if the object or an attribute is a class. 
        * ${a:1}.IsClass(a,int) -> True
        * ${a:1}.IsClass(a,str) -> False
        * ${a:1}.IsClass(a,None) -> False
        * ${a:None}.IsClass(a,int) -> False
        * ${}.IsClass(int) -> False
        * $None.IsClass(int) -> False
        '''
        if att == None:
            return isinstance(self.Obj(), cls)
        return isinstance(self.GetAtt(att), cls)


    def IsDict(self, att:str=None) -> bool:
        ''' 👉 Indicates if the object or an attribute is a dictionary. 
        * ${a:{b:1}}.IsDict(a) -> True
        * ${a:1}.IsDict(a) -> False
        * ${a:None}.IsDict(a) -> False
        * ${}.IsDict() -> False
        * $None.IsDict() -> False
        '''
        if att == None:
            return isinstance(self.Obj(), dict)
        return isinstance(self.GetAtt(att), dict)


    def Length(self) -> int:
        ''' 👉 Returns the length of the internal object.'''
        if self.IsList():
            return len(self.Obj())
        elif self.IsDict():
            return len(self.Attributes())
        elif self.IsStr():
            return len(self.Obj())
        return 0

    
    def Attributes(self) -> list[str]:
        ''' 👉 Returns the names of the attributes of the internal object. 
        * Same as Keys()
        * ${a:1, b:2}.Attributes() -> [a,b]
        '''
        ##LOG.Print(f'STRUCT({self.Obj()}).Attributes()')
        from .STRUCT import STRUCT

        # Get the object, unwraping STRUCT to infinit.
        obj:dict = self.Obj()
        while UTILS.IsType(obj, STRUCT):
            obj = obj.Obj()

        # Return empty if the object is None.
        if obj == None:
            return []
            
        # Return the keys of the object if a dictionary.
        if UTILS.IsType(obj, dict):
            return list(obj.keys())
        
        # If it's a list, return the list values.
        if UTILS.IsType(obj, list):
            return obj
        
        if type(obj).__name__ == '_Environ':
            import os
            return list(os.environ.keys())

        return []
    


    def RemoveAtt(self, name=str, safe:bool=False):
        """ 👉 Removes an attribute. 
        * ${a:1, b:2}.RemoveAtt('a') -> ${b:2}
        * ${a:{b:2}}.RemoveAtt('a.b') -> ${a:{}}
        * ${}.RemoveAtt('a') -> Exception! (attribute not found)
        """
        UTILS.RequireArgs([name])
        
        root:dict = self._obj
        parent:dict
        parts = name.split('.')
        child:str = None
        
        for part in parts:
            if part in root:
                parent = root
                UTILS.AssertIsType(given=parent, expect=dict)
                
                root = root[part]
                child = part

            elif safe == True:
                return self
            
            else:
                LOG.RaiseValidationException(f'Att [{part}] not found in [{root}]!')

        del parent[child]
        return self



    def DefaultTimestamp(self, att:str):
        """ 👉 Sets the value of an attribute to Timestamp, if not set. """
        self.Default(
            name= att, 
            default= UTILS.GetTimestamp()
        )
        self.RequireTimestamp(att= att)
        return self


    def DefaultGuid(self, name):
        """ 👉 Sets the value of an attribute to UUID, if not set. """
        self.Default(
            name= name, 
            default= UTILS.UUID())
        return self
    


    def Default(self, name:str, default:any):
        """ 👉 Sets the value of a string attribute, if not set. 
        * s=${a:1}.Default(a,2); s.Obj() -> {a:1}
        * s=${a:1}.Default(b,2); s.Obj() -> {a:1,b:2}
        * s=${a:{b:2}}.Default(a.c,3); s.Obj() -> {a:{b:2,c:3}}
        * s=${}.Default(a.c,3); s.Obj() -> Untested behaviour!
        """
        UTILS.RequireArgs([name])
        if self.IsMissingOrEmpty(name):
            self.GetAtt(name, set=default)
        return self



    def RequireStructs(self, att:str=None) -> list[STRUCT_ATTRIBUTES]:
        ''' 👉 Returns a list of structures referenced by the mandatory property. 
        * $[x,y].RequireStructs() -> [$x, $y]
        * ${a:[x,y]}.RequireStructs(a) -> [$x, $y]
        * $None.RequireStructs() -> Exception!
        * ${}.RequireStructs(a) -> Exception!
        * ${a:None}.RequireStructs(a) -> Exception!
        * ${a:[]}.Structs(a) -> []
        '''

        val = self.RequireAtt(att)
        if att == None:
            val = self.Obj()
        
        if not isinstance(val, list):
            LOG.RaiseValidationException(f'Att {att} should be a list! Found={type(val)}')

        ret = self.Structs(att)
        return ret



    def Structs(self, att:str=None) -> list[STRUCT_ATTRIBUTES]:
        ''' 👉 Returns a list of structures referenced by the property. 

        Without att:
        * $[x,y].Structs() -> [$x, $y]
        * $None.Structs() -> []

        With att:
        * ${a:[x,y]}.Structs(a) -> [$x, $y]
        * ${}.Structs(a) -> []
        * ${a:None}.Structs(a) -> []
        * ${a:[]}.Structs(a) -> []
        '''
        from .STRUCT import STRUCT

        ##LOG.Print(f'STRUCT.Structs(att={att})')
        ##LOG.Print(f'STRUCT.Structs()._obj={self._obj})')

        if att != None:
            list = self.GetAtt(att)
        else:
            list = self.Obj()

        if list == None:
            return []
        
        ret = []
        ##LOG.Print(f'STRUCT.Structs().len(list)={len(list)})')
        for element in list:
            item = STRUCT(element)
            ret.append(item)
            
        ##LOG.Print(f'STRUCT.Structs().len(ret)={len(ret)})')
        return ret
    

    def Require(self):
        ''' 👉 Throws an exception if the object is missing or empty.'''
        # raise an exception if the object is missing or empty.
        if self.IsMissingOrEmpty():
            LOG.RaiseValidationException(f'The struct should not be empty!')
        return self


    def RequireAtt(self, 
        name:str=None, 
        set:any=None, 
        default:str=None, 
        msg:str=None, 
        noHierarchy:bool=True
    ) -> any: 
        """
        👉 Gets the value from the mandatory object, or throws an exception if missing/empty. 
        * ${}.Require() -> Exception!
        * $None.Require() -> Exception!
        * $(1).Require() -> 1
        * $(False).Require() -> False

        👉 Gets the value from the mandatory attribute, or throws an exception if missing/empty. 
        * ${a:None}.Require(a) -> Exception!
        * ${a:{}}.Require(a) -> {}
        * ${a:1}.Require(a) -> 1
        * ${a:False}.Require(a) -> False
        * ${a:''}.Require(a) -> Exception!
        * ${}.Require(a, set=1) -> 1
        * ${}.Require(a, set={}) -> Exception!

        👉 To get chained atributes, use '.' for the hierarchy.
        * {a:{b:1}}.Require('a.b') -> 1

        Params:
        * att: name of the attribute within the structure - only works for dictionaries.
        * set: value to update the content.
        * default: value to be returned in case the content is empty - on empty content, default can't be empty.
        * check: message to be displayed in case of assertion failure.
        * noHierarchy: don't execute '.' separator logic, i.e. given 'A.B', look for [A.B], not [A][B].
        """
        LOG.Print(f'📦 STRUCT.Require(att={name}, set={set})', self)
        
        UTILS.AssertIsStr(name)

        if not name:
            obj = self.Obj()
            if UTILS.IsNoneOrEmpty(obj) or obj == {}:
                LOG.RaiseValidationException(f'The struct should not be empty!', msg)    
            return self

        ret = self.GetAtt(name, 
            set=set, 
            default=default, 
            noHierarchy=noHierarchy)
        
        if UTILS.IsNoneOrEmpty(ret):
            LOG.RaiseValidationException(
                f'Required attribute missing: {name=}',
                msg, f'given=({ret})', 
                f'available={self.Attributes()}', 
                f'struct=', self)
            
        return ret
        
    


    def RequireDateTime(self, att:str, default:str=None) -> datetime:
        '''👉 Gets the value from the mandatory datetime, or throws an exception if missing/invalid.'''
        val = self.GetAtt(att, default=default)
        
        if type(val) is str:
            return UTILS.ParseTimestamp(val)
        
        if type(val) is datetime:
            return val
        
        LOG.RaiseValidationException(
            f'Expected a datetime attribute {att}!', 
            f'Found type={type(val).__name__}', 
            f'val={val}', 
            f'on={self._obj}')



    def RequireTimestamp(self, att:str, set:str=None, default:str=None):
        '''👉 Gets the value from the mandatory timestamp, or throws an exception if missing/invalid.
        * Success: ${a:2023-04-01T05:00:30.001000Z}.RequireDateTime(a) -> '2023-04-01T05:00:30.001000Z'
        * Not UTC: ${a:2023-04-01T05:00:30.001000}.RequireDateTime(a) -> Exception!
        * Invalid: ${a:x}.RequireDateTime(a) -> Exception!
        * No att: $.RequireDateTime(att=None) -> Exception!
        * Else: see $.Require()
        '''
        UTILS.RequireArgs([att])

        val = self.RequireStr(att, set=set, default=default)

        if not 'Z' in val:
            LOG.RaiseValidationException(
                f'Required timestamp attribute {att} in UTC',
                f'(with ending Z, like 2023-04-01T05:00:30.001000Z)!',
                f'Found val={val}')
        
        # Verify if it's a timestamp.
        UTILS.ParseTimestamp(val)
        UTILS.Require(val)
        return val
    

    def GetBool(self, name:str, default:bool=None, set:bool=None) -> Union[bool,None]:
        '''👉 Returns a boolean or None.'''
        UTILS.AssertIsBool(default, require=False)
        val = self.GetAtt(name, default=default, set=set)
        if val == None:
            return None
        if type(val) != bool:
            LOG.RaiseValidationException('Expected a boolean!', f'{val=}', self)
        return val


    def GetInt(self, name:str, default:int=None, set:str=None) -> Union[int,None]:
        '''👉 Returns an int or None.'''
        UTILS.AssertIsInt(default, require=False)
        val = self.GetAtt(name, default=default, set=set)
        if val == None:
            return None
        if type(val) != int:
            LOG.RaiseValidationException('Expected an int!', f'{val=}', self)
        return val
    

    def GetAtt(self, 
        name: str, 
        default= None, 
        root= None, 
        set: any= None, 
        noHierarchy: bool= True,
        require: bool= False
    ) -> Union[any,None]:
        """ 
        👉 Sets or gets the value from the referenced attribute. 
        To get chained atributes, use '.' for the hierarchy.

        Getter:
        * ${a:1}.Get(a) -> 1 (gets native)
        * ${a:{b:2}}.Get(a) -> {b:2} (gets objects)
        * ${a:{b:2}}.Get(a.b) -> 2 (gets children)
        * ${}.Get(a) -> None (returns safe missing)

        Default:
        * ${}.Get(a, default=x) -> x (defaults missing)
        * s=${}; s.Get(a, default=x); s.Obj() -> {} (default is immutable)

        Setter:
        * ${}.Get(a, set=x) -> x (setter returns)
        * s=${}; s.Get(a, set=x); s.Obj() -> {a:x} (setter is mutable)
        * s=${}; s.Get(a, set=$x); s.Obj -> {a:x} (setter unboxes structs)
        """
        LOG.Print(
            f'📦 STRUCT.Att({name=}, {default=}, {root=}, {set=})', 
            f'{name=}', f'{default=}', f'{root=}', f'{set=}')
        
        UTILS.RequireArgs([name])
        UTILS.AssertIsStr(name)

        # hierarchy navigation
        if root == None:
            LOG.Print(f'📦 STRUCT.Att(): root == None',
                '_attRoot=', self._attRoot)

            # Check if the object has a _attRoot attribute.
            if hasattr(self, '_attRoot'):
                if self._attRoot:
                    root = self._attRoot

        # setter
        if set != None:
            LOG.Print(f'📦 STRUCT.Att:', 'set != None')

            if '.' in name and noHierarchy!=True:
                LOG.RaiseValidationException(
                    'Unsupported: composed names not implemented for setting!')
            
            if self._obj == None:
                LOG.RaiseException(
                    'To mitigate bugs, setting on None is not allowed!', 
                    'Initialize with ({}), or use explicit .ClearAtt() instead.', 
                    'self=', self)

            obj = self.Unstruct(set)
            #self._attRoot[name] = obj

            LOG.Print(
                f'📦 STRUCT.Att():', 
                f'setting [{name}]={obj}',
                f'on ._obj=', self)

            if type(self._obj) not in [dict]:
                LOG.RaiseException(
                    f'📦 STRUCT.Att: Only lists and dictionaries are supported here', 
                    f'found [{type(self._obj)}]', 
                    'self=', self)

            self._obj[name] = obj
            return set

        # default to the root object.
        if root == None and self._obj != None:
            LOG.Print(f'📦 STRUCT.Att(): root == None, using ({self._obj=})')
            root = self._obj

        # get on a null object.
        if root == None:

            if require == True:
                LOG.RaiseValidationException(
                    f'Attribute {name} is required, but not found!', 
                    f'{name=}', self)

            LOG.RaiseValidationException(
                f'To avoid bugs, getAtt(STRUCT(None)) is not allowed!', 
                f'{name=}', self)
        
        # root getter
        if '.' not in name or noHierarchy==True:
            LOG.Print(f'📦 STRUCT.Att:', '. not in name', 
                f'{noHierarchy=}',
                'name=', name, 'root=', root, 'self=', self)

            if isinstance(root,dict) and name in root:
                LOG.Print(f'📦 STRUCT.Att(): in root')
                val = root[name]
                if default == None:
                    LOG.Print(f'📦 STRUCT.Att(): return val1')
                    return val
                else:
                    if val == None:
                        LOG.Print(f'📦 STRUCT.Att(): return default')
                        return default
                    else: 
                        LOG.Print(f'📦 STRUCT.Att(): return val2: ', val)
                        return val
            
            # not found, look in attribute alias from the root.
            from .STRUCT import STRUCT   
            if UTILS.IsType(self._attMap, STRUCT):
                LOG.RaiseException('self._attMap should not be a STRUCT!')
            if UTILS.IsType(name, STRUCT):
                LOG.RaiseException('name should not be a STRUCT!')

            if name in self._attMap:
                LOG.Print(f'📦 STRUCT.Att(): [{name}] in _attMap', self._attMap)
                return self.GetAtt(self._attMap[name], 
                    default= default, 
                    root= self._obj,
                    noHierarchy= noHierarchy)
            
            # not found, look in the top.
            if self._obj and name in self._obj and root != self._obj:
                LOG.Print(f'📦 STRUCT.Att(): in _obj')
                return self.GetAtt(name, 
                    default=default, 
                    root=self._obj, 
                    noHierarchy=noHierarchy)
            
            LOG.Print(f'  STRUCT.Att(): default')
            return default
        
        # chained getter
        if '.' in name:
            LOG.Print(f'📦 STRUCT.Att:', '. in name')

            names = name.split('.')
            parent = self.GetAtt(name=names[0])
            names.pop(0)
            child = '.'.join(names)
            return self.GetAtt(name=child, root=parent)
    

    def RequireBool(self, 
        att:str, 
        set:bool=None, 
        default:bool=None, 
        noHierarchy:bool=True
    ) -> bool:
        """ 👉 Gets the boolean from the mandatory attribute, or throws an exception if missing/empty/non-bool. 
        
        Getter:
        * ${a:True}.RequireBool(a) -> True 
        * ${a:False}.RequireBool(a) -> False
        * ${a:{b:False}}.RequireBool(a.b) -> False  # gets children

        Setter:
        * ${}.RequireBool(a, True) -> True, ${a:True}
        * ${a:False}.RequireBool(a, True) -> True, ${a:True}
        * ${a:False}.RequireBool(a, None) -> False, ${a:False} # same as get

        Exceptions:
        * $.RequireBool(att=None) -> Exception! (requires att)
        * ${a:x}.RequireBool(a) -> Exception! (can only be bools)
        * ${}.RequireBool(a) -> Exception! (cannot not empty)
        * ${a:None}.RequireBool(a) -> Exception! (can not be null)
        """
        UTILS.RequireArgs([att])
        val = self.RequireAtt(att, 
            set=set, 
            default=default, 
            noHierarchy=noHierarchy) 
        if not isinstance(val, bool):
            LOG.RaiseValidationException(f'Required attribute {att} should be a boolean, but found ({type(val).__name__}:{val}).')
        return val


    def RequireDeepInt(self, att:str) -> int:
        '''👉 Gets the value from the mandatory int, or throws an exception if missing/invalid.'''
        return self.RequireInt(att, noHierarchy=False)


    def RequireInt(self, att:str, 
        noHierarchy:bool=True,
    ) -> int:
        '''👉 Gets the value from the mandatory int, or throws an exception if missing/invalid.'''
        UTILS.RequireArgs([att])
        val = self.RequireAtt(att, noHierarchy=noHierarchy)
        UTILS.AssertIsType(val, int)
        return val
    

    def RequireFloat(self, att:str) -> float:
        '''👉 Gets the value from the mandatory float, or throws an exception if missing/invalid.'''
        UTILS.RequireArgs([att])
        val = self.RequireAtt(att)
        UTILS.AssertIsType(val, float)
        return val


    def UUID(self, att:str, msg:str=None) -> Union[str, None]:
        '''👉 Returns a UUID attribute of the struct, or None.'''
        
        val = self.GetStr(att)
        if val == None:
            return val

        if UTILS.IsUUID(val) != True:
            LOG.RaiseValidationException(
                f'Required attribute {att} should be a UUID, but found=({val})',
                msg, self)
        return val


    def RequireDeepUUID(self,
        att:str,
        set:str=None,
        msg:str=None,
    ) -> str:
        return self.RequireUUID(att, set=set, msg=msg, noHierarchy=False)   


    def RequireUUID(self, 
        att:str, 
        set:str=None, 
        msg:str=None,
        noHierarchy:bool=True
    ) -> str:
        '''👉 Returns a UUID attribute of the struct, 
              or raises an error if not UUID or not exists.
    
        Params
        * att: name of the attribute.
        * set: new value to set.
        * msg: additional exception message.
        '''
        
        val = self.RequireStr(att, 
            set=set, 
            noHierarchy=noHierarchy)

        if UTILS.IsUUID(val) != True:
            LOG.RaiseValidationException(
                f'Required attribute {att} should be a UUID, but found=({val})',
                msg, self)
        return val


    def RequireDeepStruct(self,
        att:str,
        msg:str=None,
    ):
        return self.RequireStruct(att, 
            msg=msg, 
            noHierarchy=False)


    def RequireDeepStr(self, 
        att:str, 
        default:str=None, 
        msg:str=None
    ) -> str:
        return self.RequireStr(att, 
            default=default, 
            msg=msg, 
            noHierarchy=False)


    def RequireStr(self, 
        att:str, 
        set:str=None, 
        default:str=None, 
        msg:str=None, 
        noHierarchy:bool=True
    ) -> str:
        '''👉 Gets the value from the mandatory string, or throws an exception if missing/invalid.
        
        Getter usage:
        * ${a:'x'}.RequireStr(a) -> 'x'
        * ${a:{b:'x'}}.RequireStr(a.b) -> 'x'

        Setter usage:
        * s=${}; s.RequireStr(a, 'x'); s.Obj() -> {a:'x'}
        * s=${a:'x'}; s.RequireStr(a, 'y'); s.Obj() -> {a:'y'}
        * s=${a:{}}; s.RequireStr(a.b, 'y'); s.Obj() -> {a:{b:'y'}}
        * s=${}; s.RequireStr(a.b, 'y'); s.Obj() -> Untested behaviour!

        Exceptions:
        * $.RequireStr(att=None) -> Exception! (attribute name is required)
        * ${}.RequireStr(a) -> Exception! (should exist)
        * ${a:True}.RequireStr(a) -> Exception! (should be a string)
        * ${a:'  '}.RequireStr(a) -> Exception! (should not be empty)
        * ${a:'x'}.RequireStr(a, True) -> Exception! (setter should be a string)
        '''
        UTILS.RequireArgs([att])

        if set != None:
            if set == str:
                LOG.RaiseException(
                    f'Check your code, you have (set=str)! It should be (set:str=None).', msg)
            UTILS.AssertIsType(set, str)

        val = self.RequireAtt(
            name= att, 
            set= set, 
            default= default, 
            msg= msg, 
            noHierarchy= noHierarchy)

        if not isinstance(val, str):
            LOG.RaiseValidationException(
                f'Attribute [{att}] should be a string!', 
                f'{msg=}', 
                f'Found= {type(val).__name__}:{val}',
                'on=', self)
        
        if str(val).strip() == '':
            LOG.RaiseValidationException(
                f'Required string attribute [{att}] should not be empty on={self._obj}.', msg)
        
        return val
    

    def SetBool(self, name:str, set:bool):
        '''👉 Sets the value from the referenced attribute. '''
        UTILS.AssertIsBool(set)
        self.SetAtt(name= name, set= set)
        return self


    def SetAtt(self, name:str, set:any):
        '''👉 Sets the value from the referenced attribute. '''
        #self.Att(name= name, set= set)
        if self._obj != {}:
            self.Require()
        self._obj[name] = set
        return self


    def ClearAtt(self, att:str):
        '''👉 Changes or initializes an attribute to None.'''
        #if att not in self._obj:
        #    LOG.ValidationException(f'No top attribute [{att}] found in={self._obj}')
        self._obj[att] = None


    def GetStr(self, name:str, default:str=None, set:str=None) -> Union[str,None]:
        '''👉 Returns a string or None.'''
        val = self.GetAtt(name, default=default, set=set)
        UTILS.AssertIsType(val, str)
        return val
    

    def GetTimestamp(self, name:str, default:str=None, set:str=None) -> Union[str,None]:
        '''👉 Returns a timestamp or None.'''
        val = self.GetAtt(name, default=default, set=set)
        if val == None:
            return None
        if not UTILS.IsTimestamp(val):
            LOG.RaiseValidationException('Expected a timestamp!', f'{val=}', self)
        return val




    def Match(self, att:str, value:any, msg:str=None):
        """ 👉 Checks if the referenced attribute value equals the given value. 
        * ${a:1}.Match(a, 1) -> OK
        * ${a:1}.Match(a, 2) -> Exception!
        * ${}.Match(a, {}) -> Exception!
        * $None.Match(a, None) -> Exception!
        * ${a:1}.Match(None, 1) -> Exception!
        """
        UTILS.RequireArgs([att])
        if self.RequireAtt(att) != value:
            LOG.RaiseValidationException(
                f'Unexpected value for {att}!',
                f'self[{att}]= `{self.RequireAtt(att)}`',
                f'but expected= `{value}`',
                msg, self)
        return self


    def GetDict(self, att:str=None, default:dict=None, set:dict=None) -> dict:
        '''👉 Returns a dictionary or None.'''
        if att == None: 
            val = self.Obj()
        else:
            val = self.GetAtt(att, default=default, set=set)
        UTILS.AssertIsType(val, dict)
        return val


    def RequireDict(self, att:str, set:dict=None, msg:str=None) -> dict:
        '''👉 Gets the value from the mandatory dict, or throws an exception if missing/invalid.'''
        val = self.RequireAtt(att, set=set, msg=msg)
        UTILS.AssertIsType(val, dict)
        return val


    def RequireStruct(self, 
        att:str, 
        set:any=None, 
        msg:str=None, 
        noHierarchy:bool=True
    ):
        """ 👉 Sets or gets the structure referenced by the mandatory property. 

        Usage:
        * ${a:x,b:y}.RequireStruct(a) -> $x (direct)
        * ${a:{b:y}}.RequireStruct(a.b) -> $y (children)

        Exceptions:
        * ${b:y}.RequireStruct(a) -> Exception! (att must exist)
        * ${a:None}.RequireStruct(a) -> Exception! (att cannot be null)
        * ${a:{}}.RequireStruct(a) -> Exception! (att cannot be empty)
        * ${a:' '}.RequireStruct(a) -> Exception! (att cannot be an empty string)
        * ${}.RequireStruct(a) -> Exception! (the struct cannot be empty)
        * ${}.RequireStruct(None) -> Exception! (the att name must be provided)

        Parameters:
        * noHierarchy: don't execute '.' separator logic, i.e. given 'A.B', look for [A.B], not [A][B].
        """
        UTILS.RequireArgs([att])
        
        if set == None:
            self.Require()
        val = self.RequireAtt(att, set=set, msg=msg, noHierarchy=noHierarchy)
        UTILS.Require(val)
        
        if isinstance(val, STRUCT_ATTRIBUTES):
            val = val.Obj()

        UTILS.AssertIsType(
            given=val, 
            expect=dict, 
            msg=f'Att [{att}] should be a dict, but found type={type(val).__name__}, val={val}, msg={msg} !')
        
        from .STRUCT import STRUCT
        return STRUCT(val)
    

    def GetStruct(self, 
        att:str, 
        default:dict=None, 
        set:dict=None,
        noHierarchy:bool=True
    ):
        """ 
        👉 Returns the structure referenced by the property.
        * ${a:x,b:y}.Struct(a) -> $x
        * ${a:{x:1},b:y}.Struct(a.x) -> $1 (reads children)
        * ${}.Struct(a) -> $None (safe missing)
        * $None.Struct(a) -> $None (safe missing)
        * ${a:x}.Struct(b) -> $None (safe missing)
        * ${a:x}.Struct(None) -> Exception! (the att name must be provided)
        """
        from .STRUCT import STRUCT

        # Get the value from the attribute.
        UTILS.RequireArgs([att])

        # Get the value from the attribute.
        val = self.GetAtt(att, 
            default=default, 
            set=set, 
            noHierarchy=noHierarchy)
        
        # Box the value if it's a dict.
        return STRUCT(val)
    
