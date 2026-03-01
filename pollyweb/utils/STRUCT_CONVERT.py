from typing import Union
from .FILE import FILE
from .STRUCT_BASE import STRUCT_BASE
from .UTILS import UTILS 
from .LOG import LOG
import json


class STRUCT_CONVERT(
    STRUCT_BASE
):
    
    

    def ToYaml(self, indent:int=0) -> str:
        ''' 👉 Converts the inner object into a YAML string.'''
        return UTILS.ToYaml(self._obj, indent=indent)

    
    def __to_json__(self):
        return self.Obj()
    

    def __repr__(self):
        return f'{self.__str__()}'
    


    def Raw(self):
        ''' 👉 Returns a json dumps+loads to remove any internal structs. '''
        return UTILS.Raw(self.Obj())
    



    def __str__(self):
        ''' 👉 Returns the inner object to be used in LOG.Print(f'{my_struct}'). 
        * LOG.Print(${a:1}) -> '{a:1}'
        * LOG.Print($None) -> ''
        '''
        
        if not hasattr(self, '_obj'):
            raise Exception(
                'STRUCT_CONVERT: Missing _obj attribute.'
                ' Have you initialized the objec?')
        
        if isinstance(self._obj, dict):
            return json.dumps(self.Obj(), indent= 2)
        else:
            return f'{self.Obj()}'



    def Print(self, title=None):
        ''' 👉 Prints the json representation of the inner object. 
        * ${a:1}.Print() -> '={a:1}'
        * ${a:1}.Print('myvar') -> 'myvar={a:1}'
        '''
        LOG.Print(f'🖨️ STRUCT.Print()', 
                  f'{title=}', self)
        


    def Copy(self):
        """ 👉 Returns a deep copy of the internal object. 
        * ${a:{x:1}}, b=a.Copy(); b.Att(x)=2; a.Print() -> '={a:{x:1}}'
        * ${a:{x:1}}, b=a; b.Att(x)=2; a.Print() -> '={a:{x:2}}'
        """
        from .STRUCT import STRUCT
        from copy import deepcopy
        clone = deepcopy(self.Obj())
        return STRUCT(clone)
    


    @classmethod
    def CastList(cls, lst:list[any]):
        '''👉 Casts a list of objects into the class type.'''
        return [
            cls.Cast(item) 
            for item in lst
        ]


    @classmethod 
    def Cast(cls, obj:any):
        '''👉 Casts the object into the class type, 
        or fails if types dont match.'''
        UTILS.AssertIsType(obj, cls, 
            msg='🤔 Are you looking for STRUCT.Parse() instead?')
        return cls(obj)
    

    @classmethod 
    def Parse(cls, obj:any):
        '''👉 Wraps the object into the class type.'''
        ret = cls()
        ret.Obj(obj)
        return ret
    

    @classmethod
    def ParseList(cls, lst:list[any]):
        '''👉 Wraps a list of objects into the class type.'''
        return [
            cls.Parse(item) 
            for item in lst
        ]


    def __to_yaml__(self, indent:int=0) -> str:
       ''' 👉 Converts the inner object into a YAML string.'''
       return UTILS.ToYaml(self.Raw(), indent=indent)
        

    def LoadYamlFile(self, path:Union[str, FILE]):
        ''' 👉 Loads the internal object from a YAML file. '''
        
        UTILS.AssertIsAnyType(path, [str, FILE], require=True)

        if isinstance(path, FILE):
            yaml = path.ReadYaml()
        else:
            yaml = UTILS.OS().File(path).ReadYaml()

        self.Obj(yaml)


    def Canonicalize(self) -> str:
        ''' 👉️ Compacts, removing spaces and line breaks.
        * Source: https://bobbyhadz.com/blog/python-json-dumps-no-spaces 
        * ${ a: 1, b: 2 }.Canonicalize() -> '{a:1,b:2}'
        '''
        return UTILS.Canonicalize(self._obj)
    

    def ToJson(self, indent:int=None) -> str:
        ''' 👉 Converts the inner object into a JSON string.
        * ${a:1,b:2}.ToJson() -> '{ a: 1, b: 2 }'
        '''
        return UTILS.ToJson(self, indent=indent)
        #return UTILS.ToJson(self._obj)


    

    @classmethod
    def AssertClass(cls, value:any, require:bool=False):
        '''👉 Raises an error if the type of the given value is not the same as the class.'''
        
        if value == None:
            if require == True:
                LOG.RaiseValidationException(
                    f'Missing required value of type={cls.__name__}')
            return
        
        UTILS.AssertIsType(
            given= value, 
            expect= cls)
