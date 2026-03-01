from typing import Union
import json

class PRINTABLE:
    '''👉️ A class that can be serialized to JSON.'''
        

    def __init__(self, toJson:Union[str, callable]=None) -> None:
        '''👉️ Initializes a class that can be serialized to JSON.
            * Carefull not to use functions.
            * Use only properties to avoid infinit loops.
        '''

        from .LOG import LOG
        
        # Validate the toJson argument.
        if toJson is None:
            from .UTILS import UTILS
            from dataclasses import asdict
            self._to_json = lambda: UTILS.ToJson(asdict(self))
            
        elif isinstance(toJson, str):
            self._to_json = lambda: toJson

        elif callable(toJson):
            self._to_json = toJson

        elif isinstance(toJson, dict):
            self._to_json = lambda: toJson

        else:
            LOG.RaiseException(
                '@: Invalid toJson argument.', toJson)

        # Test the class.
        self._TestIt()


    def _TestIt(self):
        # Test (this is veeeeery slow).
        return
        from .LOG import LOG
        if not LOG.Settings().GetTestFast():
            self.__repr__()
            self.__to_yaml__(indent=2)


    def ToYaml(self, indent:int=0) -> str:
        '''👉️ Returns the YAML representation of the object.'''
        return self.__to_yaml__(indent=indent)

    
    def _ToObj(self) -> any:
        '''👉️ Returns the object.'''
        
        # Verify of the method exists.
        if not hasattr(self, '_to_json'):
            return self.__dict__
            #return '<no _to_json method>'
        
        # Verify if the method is callable.
        if not callable(self._to_json):
            return '<_to_json is not callable>'
        
        # Return the object.
        return self._to_json()
        

    def __to_json__(self) -> str:
        '''👉️ Returns the JSON representation of the object.'''
        
        return self._ToObj()
        

    def __str__(self):
        '''👉️ Returns the string representation of the object.'''

        obj = self._ToObj()

        # Return the JSON representation of a dictionary.
        if isinstance(obj, dict):    
            ret = json.dumps(obj)
        elif isinstance(obj, str):
            ret = obj
        elif isinstance(obj, list):
            ret = obj
        else:
            ret = f'{obj}'

        if not isinstance(self, PRINTABLE):
            ret = f'{ret} <{self.__class__.__name__}>'
        return ret


    def __repr__(self) -> str:
        '''👉️ Returns a beautified string representation of the object.'''

        obj = self._ToObj()

        # Return the JSON representation of a dictionary.
        if isinstance(obj, dict):    
            ret = json.dumps(obj, indent= 2)
            if len(ret.splitlines()) > 20:
                # If the JSON is too long, return the object for an in-line print.
                ret = obj
        elif isinstance(obj, str):
            ret = obj
        elif isinstance(obj, list):
            ret = obj
        else:
            ret = f'{obj}'

        if not isinstance(self, PRINTABLE):
            ret = f'{ret} <{self.__class__.__name__}>'
            
        return str(ret)


    def __to_yaml__(self, indent:int=0) -> str:
        '''👉️ Returns the YAML representation of the object.'''
        from .UTILS import UTILS
        json = self._ToObj()
        return UTILS.ToYaml(json, indent=indent)
    

    @classmethod
    def LOG(cls):
        '''👉 Returns the LOG class.'''
        from .LOG import LOG
        return LOG
        
    
    @classmethod
    def UTILS(cls):
        '''👉 Returns the UTILS class.'''
        from .UTILS import UTILS
        return UTILS
    

    @classmethod
    def TESTS(cls):
        '''👉 Returns the TESTS class.'''
        from .TESTS import TESTS
        return TESTS