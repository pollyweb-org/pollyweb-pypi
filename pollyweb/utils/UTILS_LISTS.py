# 📚 UTILS

from typing import List, Dict, Union

from .LOG import LOG
from .UTILS_OBJECTS import UTILS_OBJECTS
from .UTILS_TYPES import UTILS_TYPES


class UTILS_LISTS(UTILS_TYPES, UTILS_OBJECTS): 
    '''👉️ Generic methods.'''


    @classmethod
    def RequireStrings(cls, value:list[str]) -> list[str]:
        ''' 👉 Returns the value if it is a list of strings, or raises an exception.'''
        cls.Require(value)
        if not isinstance(value, list):
            LOG.RaiseValidationException(f'Not a list: {value}!')
        for v in value:
            if not isinstance(v, str):
                LOG.RaiseValidationException(f'Not a string: {v}!')
        return value
    

    @classmethod
    def AssertContains(cls, lst:list, value:str, msg:str=None):
        '''👉️ Checks if a list contains a value, or raises an exception.'''
        cls.RequireArgs([lst, value])
        cls.AssertIsType(lst, list)
        if value not in lst:
            LOG.RaiseValidationException(f'Value not found in list!', 
                f'{value=}', 
                f'{lst=}', msg)


    @classmethod
    def AssertIsAnyValue(cls, 
        value:Union[str,int], 
        options:list[Union[str,int]], 
        msg:str=None
    ):
        '''👉️ Raises an exception if the the given value is not on the options.
        * MatchAny(a, [a,b,c]) -> OK
        * MatchAny(d, [a,b,c]) -> Exception
        '''
        cls.RequireArgs([value])
        if value not in options:
            LOG.RaiseValidationException(f'📦 UTILS.MatchAny:', 
                f'Value={type(value).__name__}:({value}) is not an option.',
                f'Use one of {options}.', msg)
     

    @classmethod
    def Length(cls, value:Union[str, list, dict]) -> int:
        '''👉️ Returns the length of an str, list, or dict.'''

        from .STRUCT import STRUCT
        if value and isinstance(value, STRUCT):
            value = value.Obj()

        cls.Require(value)
        cls.AssertIsAnyType(value, [list, str, dict])
        if isinstance(value, str):
            return len(value.strip())
        elif isinstance(value, list):
            return len(value)
        elif isinstance(value, dict):
            return len(value.keys())    
        else:
            LOG.RaiseValidationException(
                f'Unexpected type: {type(value).__name__}.')


    @classmethod
    def AssertLenght(cls, value:Union[str,list], expectedLength:int, msg:str=None):
        '''👉️ Checks if a list is of a given lenght, or raises an exception.
        * MatchLenght([], 0) -> OK
        * MatchLenght([], 1) -> Exception
        '''

        if isinstance(value, str):
            given = len(value.strip())
        elif isinstance(value, list):
            given = len(value)
        else:
            LOG.RaiseValidationException(
                f'📦 UTILS.MatchLenght: Unexpected type=({type(value).__name__}) for value=({value}).')
            
        if given != expectedLength:
            LOG.RaiseValidationException(
                f'📦 UTILS.MatchLenght: Expected lengh [{expectedLength}] but found [{given}].', msg)
        

    @classmethod
    def AssertIsList(cls, 
        val:list, 
        itemType:type= None,
        require:bool= False, 
        msg:str= None, 
        size:int= None
    ):
        '''👉️ Checks if a value is in a list, or raises an exception.
        
        Parameters:
         * `val` (list): The list to be checked.
         * `itemType` (type): The expected type of the items in the list.
         * `require` (bool): If True, the list should not be empty.
         * `msg` (str): The message to be displayed in case of an exception.
         * `size` (int): The expected size of the list.
        '''

        LOG.Print('📦 UTILS.LISTS.EnsureIsList:', val, require)

        # Validate the arguments.
        cls.AssertIsBool(require)
        cls.AssertIsInt(size)

        # Check if the value is required.
        if require == True:
            cls.Require(val, 
                msg=msg or f'Expected a non-empty list of {itemType.__name__ if itemType else None} objects.')

            # Ensure there are no None items.
            for item in val:
                if item == None:
                    LOG.RaiseValidationException(
                        f'📦 UTILS.MatchList: None item found in list! {val=}')

        # Check if the value is a list.
        cls.AssertIsType(val, list, 
            msg='The value should be a list.')

        # Check the size.
        if size != None:    
            cls.AssertLenght(val, size, 
                msg=f'Expected a list of size {size}.')

        # Check if the items are of a specific class.
        if val != None and itemType != None:
            for item in val:
                cls.AssertIsType(item, itemType, 
                    msg=f'The items should be of type={itemType.__name__}.')
                
        return cls
        

    @classmethod
    def ContainsAll(cls, lst:list, vals:list):
        '''👉️ Checks if a list contains all of the given valus.
        * ContainsAll([1,2,3], [1,2]) -> True
        * ContainsAll([1,2,3], [1,6]) -> False
        * ContainsAll([1,2,3], [5,6]) -> False
        * ContainsAll([], [1]) -> False
        '''
        cls.RequireArgs([lst, vals])
        cls.AssertIsType(lst,list)
        cls.AssertIsType(vals,list)

        for val in vals:
            if val not in lst:
                return False
        return True


    @classmethod
    def ContainsAny(cls, lst:list, vals:list):
        '''👉️ Checks if a list contains any of the given valus.
        * ContainsAny([1,2,3], [1,6]) -> True
        * ContainsAny([1,2,3], [0,3]) -> True
        * ContainsAny([1,2,3], [5,6]) -> False
        * ContainsAny([], [1]) -> False
        '''
        cls.RequireArgs([lst, vals])
        cls.AssertIsType(lst,list)
        cls.AssertIsType(vals,list)

        for val in vals:
            if val in lst:
                return True
        return False
    

    @classmethod
    def AppendIfMissing(cls, lst:list, obj:any):
        cls.Require(obj)
        cls.AssertIsType(lst, list)
        if obj not in lst:
            lst.append(obj)


    @classmethod
    def Distinct(cls, lst:list):
        cls.AssertIsType(lst, list)
        ret = []
        for obj in lst:
            if obj not in ret:
                ret.append(obj)
        return ret


    @classmethod
    def VerifyDuplicates(cls, lst:list):
        if lst == None: return
        cls.AssertIsType(lst, list)

        unique = []
        for obj in lst:
            obj = cls.Raw(obj)
            if type(obj) == bool:
                obj = f'<{str(obj)}>'
            if obj not in unique:
                unique.append(obj)

        cls.AssertEqual(
            given= len(lst),
            expect= len(unique),
            msg= f'📦 UTILS.LISTS.Match: Duplicate found!\n lst={cls.Raw(lst)},\n {unique=}')
        

    @classmethod 
    def RequireList(cls, value):
        ''' 👉 Returns the value if it is a list, or raises an exception.'''
        cls.Require(value)
        if not isinstance(value, list):
            LOG.RaiseValidationException(f'Not a list: {value}!')
        return value
    

    @classmethod
    def DictFromList(cls, lst:list, key:str):
        '''👉 Returns a dictionary from a list of objects.
        
        Example 1:
        ```python
            lst = [{'a': 1}, {'a': 2}]
            print(STRUCT.DictFromList(lst, key='a'))
            # Output: {'1': {'a': 1}, '2': {'a': 2}}
        ```

        Example 2:
        ```python
            class CLASS(STRUCT):
                def GetKey(self):
                    return self.GetAtt('a')
            lst = [
                CLASS({'a':'1'}),
                CLASS({'a':'2'}),
            ]
            print(STRUCT.DictFromList(lst, key='GetKey'))
            # Output: {'1': {'a': 1}, '2': {'a': 2}}

        '''
        
        from .STRUCT import STRUCT
        mylist = STRUCT(lst).GetList()
        
        # Initialize the return dictionary.
        ret = {}

        # Verify if all items are a dict or STRUCT.
        for obj in mylist:
            if not cls.IsAnyClass(obj, [dict, STRUCT]):
                LOG.RaiseValidationException(
                    f'UTILS.DictFromList: Item should be a dict or STRUCT: {obj}', 
                    'list=', lst) 

        # Iterate through the list, adding the objects to the dictionary.
        for obj in mylist:

            # Check if the key is a function. If it is, get the value from the object.
            if callable(key):
                index = key(obj)
                ret[index] = obj
                continue

            # Check if key is a method in the object, and get its value if it is.
            if hasattr(obj, key):
                index = getattr(obj, key)()
                # Get the key from the object.
                ret[index] = obj
                continue

            # Check if the key is in the object.
            if not key in obj:
                raise Exception(f'Key {key} not found in object {obj}!')    
        
            # Get the key from the object.
            ret[obj[key]] = obj

        # Return the dictionary.
        from .STRUCT import STRUCT
        return STRUCT(ret)
    

    @classmethod
    def SortList(cls, lst:list, key:str=None):
        '''👉 Sorts a list of objects by a key.'''

        from .UTILS import UTILS
        UTILS.AssertIsList(lst)

        if list == []:
            return []

        def Sorter(obj):
            
            if callable(key):
                return key(obj)
            
            if hasattr(obj, key):
                return getattr(obj, key)()
        
            if key in obj:
                return obj[key]
            
            from .STRUCT import STRUCT
            STRUCT(obj).RequireAtt(key)
            
            LOG.RaiseValidationException(f'Key `{key}` not found in object!', 
                f'key= {key}', 
                'obj=', obj,
                'lst=', lst)
        
        if key == None:
            return sorted(lst)
        else:
            return sorted(lst, key=Sorter)


    @classmethod
    def ReverseStrList(cls, lst:list[str]):
        '''👉 Reverses a list.'''
        
        if lst == None:
            LOG.RaiseValidationException('A list is required!')
            
        cls.AssertIsList(lst, itemType=str)
        arr:list[str] = cls.Copy(lst)
        arr.reverse()
        return arr
        

    @classmethod
    def RemoveEmptyStrings(cls, lst:list[str]):
        '''👉 Removes empty strings from a list.'''
        if lst == None:
            return None
        return [x for x in lst if x.strip()]
