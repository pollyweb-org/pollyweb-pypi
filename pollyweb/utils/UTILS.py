# 📚 UTILS

from .UTILS_LISTS import UTILS_LISTS
from .UTILS_PYTHON import UTILS_PYTHON
from .UTILS_TYPES import UTILS_TYPES
from .UTILS_YAML import UTILS_YAML
from .UTILS_OS import UTILS_OS
from .UTILS_TIME import UTILS_TIME
from .UTILS_OBJECTS import UTILS_OBJECTS
from .UTILS_CACHE import UTILS_CACHE
from .UTILS_CRYPTOGRAPHY import UTILS_CRYPTOGRAPHY


class UTILS(
    UTILS_PYTHON,
    UTILS_OS, 
    UTILS_YAML, 
    UTILS_TIME, 
    UTILS_LISTS,
    UTILS_TYPES,
    UTILS_OBJECTS,
    UTILS_CRYPTOGRAPHY
    ): 
    '''👉️ Generic methods.'''
           

    @classmethod
    def OS(cls):
        '''👉️ Generic methods to work with the file system.'''
        return UTILS_OS()
    

    @classmethod
    def PYTHON(cls):
        '''👉️ Generic methods to work with the file system.'''
        return UTILS_PYTHON()
    
    
    @classmethod
    def CACHE(cls, path:str=None, goUp:int=0):
        '''👉️ Generic methods to work with cache files.'''
        return UTILS_CACHE(path, goUp=goUp+1)
    

    @classmethod
    def CRYPTOGRAPHY(cls):
        '''👉️ Generic methods to work with cryptography.'''
        from .UTILS_CRYPTOGRAPHY import UTILS_CRYPTOGRAPHY
        return UTILS_CRYPTOGRAPHY()
    

    @classmethod
    def Environment(cls, name: str):
        '''👉️ Returns a configuration from os.environ, 
        i.e. same as 'os.environ[name]'.'''
        return cls.OS().Environment(name)

    
    @classmethod
    def TIME(cls):
        '''👉️ Generic methods to work with time.'''
        return UTILS_TIME()