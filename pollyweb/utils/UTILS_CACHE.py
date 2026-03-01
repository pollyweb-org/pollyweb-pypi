# 📚 CACHE

from .UTILS_OS import UTILS_OS
from .LOG import LOG
from .UTILS_PYTHON import UTILS_PYTHON


class UTILS_CACHE: 
    '''👉️ Generic methods to work with cache files.'''


    def __init__(self, path:str=None, goUp:int=0) -> None:

        if not path:
            name = UTILS_PYTHON.GetCallerClassName(goUp=goUp+1)
            path = f'__cache__/{name}.yaml'

        self._file = UTILS_OS.File(path)


    def Get(self, key:str):
        ''' 👉 Get a key from cache.'''
        
        if not self._file.Exists(): return {}
        
        from .STRUCT import STRUCT
        cache = STRUCT(self._file.ReadYaml())
        
        if cache == None:
            raise Exception('Unexpected null in cache file!')
        
        ret = cache.GetAtt(key, noHierarchy=True)
        
        return ret
    

    def Require(self, key:str):
        ret = self.Get(key)
        if ret == None:
            raise Exception('Unexpected null in cache context!')
        return ret


    def Save(self, cache):
        ''' 👉 Saves all cache.'''
        self._file.GetParentDir().Touch()
        self._file.WriteYaml(cache)


    def Set(self, key:str, value:any):
        ''' 👉 Persists a value in cache.'''
        
        from .STRUCT import STRUCT
        if self._file.Exists():
            cache = STRUCT(self._file.ReadYaml())
        else:
            cache = {}

        cache[key] = value
        self.Save(cache)    
        