# 📚 UTILS

from typing import List, Dict, Union

from .LOG import LOG
from .UTILS_OBJECTS import UTILS_OBJECTS


class UTILS_TYPES(UTILS_OBJECTS): 
    '''👉️ Generic methods.'''
    

    @classmethod
    def RequireFloat(cls, value):
        cls.Require(value)
        if not cls.IsFloat(value):
            LOG.RaiseValidationException(f'Not a float: {value}!')
        return float(value)


    @classmethod
    def IsUUID(cls, value:str) -> Union[None,bool]:
        '''👉️ Checks if a value is in a UUID.'''

        if value == None:
            return None
        
        elif value in ['<uuid>']:
            # Support correlation tests.
            return True
        
        elif type(value) != str:
            return False
        
        elif value.startswith('<session-uuid') or value.endswith('-uuid>'):
            # Support session tests.
            return True
                
        elif len(value) != len('17880417-f90c-44e1-a3f0-772441530dca'):
            return False
        
        elif '-' not in value:
            return False
        
        else:
            return True
    

    @classmethod
    def AssertIsUUID(cls, val:str, require:bool=False):
        '''👉️ Checks if a value is in a UUID, or raises an exception.'''

        if val == None:
            if require == True:
                cls.Require(val)

        elif cls.IsUUID(val) != True:
            LOG.RaiseValidationException(
                f'📦 MatchUUID: Value should be a UUID, but found=({val}).')


    @classmethod
    def AssertIsCallable(cls, val:callable, require:bool=False):
        '''👉️ Checks if a value is a function, or raises an exception.'''
        # We cannot use cls.AssertIsType() 
        #  because it doesn't consider callable as a type.
        if require == True:
            cls.Require(val)
        if val == None:
            return
        if not callable(val):
            LOG.RaiseValidationException(
                f'Expected a function [{val}] but received [{type(val).__name__}]!')


    @classmethod
    def AssertIsDict(cls, val:dict, require:bool=False, itemType:type=None):
        '''👉️ Checks if a value is in a dictionary, or raises an exception.'''

        # Validate the arguments.
        cls.AssertIsBool(require)

        # Check if the value is required.
        if require == True:
            cls.Require(val)

        # Check if the value is a dictionary.
        from .STRUCT import STRUCT
        cls.AssertIsAnyType(val, [dict, STRUCT], 
            msg='The value should be a dictionary.')

        # Check if the items are of a specific class.
        if itemType != None:
            for key in STRUCT(val).Attributes():
                cls.AssertIsType(val[key], itemType, 
                    msg='The items should be of a specific class.')


    @classmethod
    def IsInt(cls, value:int) -> bool:
        ''' 👉 Returns true if the value is an int. '''
        if isinstance(value, float):
            return False
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
        
    
    @classmethod
    def IsFloat(cls, value:float) -> bool:
        ''' 👉 Returns true if the value is a float. '''
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
        

    @classmethod
    def RequireInt(cls, value:int) -> int:
        ''' 👉 Returns the value if it is an int, or raises an exception.'''
        cls.Require(value)
        if not cls.IsInt(value):
            LOG.RaiseValidationException(f'Not an int: {value}!')
        return int(value)
    

    @classmethod
    def RequireString(cls, value:str) -> str:
        ''' 👉 Returns the value if it is a string, or raises an exception.'''
        cls.Require(value)
        if not isinstance(value, str):
            LOG.RaiseValidationException(f'Not a string: {value}!')
        return str(value)
    


    @classmethod
    def AssertIsAnyType(cls, 
        given:any, 
        options:list[type], 
        require:bool=False,
        msg:str=None
    ):
        '''👉️ Raises an exception if the the given class is not on the options.
        * MatchAnyClass('a', [str,list,dict]) -> OK
        * MatchAnyClass('a', [list,dict]) -> Exception
        '''
        
        if given == None:
            if require == True:
                cls.Require(given)
            return
        
        cls.RequireArgs([options])
        cls.AssertIsType(options, list)
        
        for option in options:
            if cls.IsType(given=given, expect=option):
                return
            
        LOG.RaiseValidationException(
            f'📦 MatchAnyClass:', 
            f'Type=({type(given).__name__}) is not an option.', 
            f'Use one of {[t.__name__ for t in options]}.', 
            msg, given)
        

    @classmethod
    def IsAnyClass(cls, given:any, options:list[type]) -> Union[None,bool]:
        '''👉️ Checks if the the given class is on the options.
        * IsAnyClass('a', [str,list,dict]) -> True
        * IsAnyClass('a', [list,dict]) -> False
        '''
        if given == None:
            return None
        for option in options:
            if cls.IsType(given=given, expect=option):
                return True 
        return False


    @classmethod
    def IsType(cls, given:any, expect:type) -> Union[None,bool]:
        '''👉️ Checks if the the given value is of a class.
        * IsClass(None, X) -> None
        * IsClass(False, bool) -> True
        * IsClass(False, int) -> False
        * IsClass(dict, dict) -> True
        * IsClass(STRUCT, dict) -> True
        '''

        if isinstance(given, type):
            LOG.RaiseException('📦 IsClass: Give a value, not a class!')

        # Don't check nulls.
        if given == None:
            return None
        
        if isinstance(given, bool) or isinstance(given, int):
            # For native types, compare the type exactly to avoid True==1.
            return type(given) == expect
            
        # For others, allow inheritance.
        if isinstance(given, expect):
            return True
        
        if issubclass(type(given), expect):
            return True
        
        return False


    @classmethod
    def AssertStrings(cls, strings:list[str], require:bool=False):
        '''👉️ Checks if a list of strings is all strings.
        * MatchStrings(['a', 'b', 'c']) -> OK
        * MatchStrings(['a', 1, 'b']) -> Exception
        '''
        cls.RequireArgs([strings])
        cls.AssertIsType(strings, list)
        
        for t in strings:
            cls.AssertIsType(t, str)
            if require == True:
                cls.Require(t)


    @classmethod
    def IsString(cls, value:str) -> bool:
        '''👉️ Checks if a value is a string.'''
        return isinstance(value, str)


    @classmethod
    def AssertIsStr(cls, value:str, require:bool=False):
        '''👉️ Checks if a value is a string, or raises an exception.'''
        if require == True:
            cls.Require(value)
        if value == None:
            return None
        cls.AssertIsType(value, str, msg='The value should be a string.')
        return str(value)


    @classmethod
    def AssertIsInt(cls, value:int, require:bool=False):
        '''👉️ Checks if a value is an integer, or raises an exception.'''
        if require == True:
            cls.Require(value)
        if value == None:
            return None
        cls.AssertIsType(value, int, msg='The value should be an integer.')
        return int(value)


    @classmethod
    def AssertIsBool(cls, value:bool, require:bool=False):
        '''👉️ Checks if a value is a boolean, or raises an exception.'''
        if require == True:
            cls.Require(value)
        if value == None:
            return None
        cls.AssertIsType(value, bool, msg='The value should be a boolean.')
        return bool(value)


    @classmethod
    def AssertIsType(cls, 
        given:any, 
        expect:type, 
        msg:str=None, 
        require:bool=False
    ):
        '''👉️ Checks if an object is of a given type, or raises an exception.
        * MatchClass('a', str) -> OK
        * MatchClass({}, dict) -> OK
        * MatchClass(STRUCT({}), dict) -> OK
        * MatchClass('a', int) -> Exception
        '''
        
        # Validate the arguments.
        if isinstance(expect, list):
            return cls.AssertIsAnyType(given, expect, require=require)
        
        if not isinstance(expect, type):
            LOG.RaiseValidationException(
                f'Type should be a class, but is `{expect}`!')

        # If it's a function, return False.
        if callable(given):
            LOG.RaiseValidationException(
                f'📦 MatchClass:', 
                f'Given type={given.__name__} is a function, not a class.', 
                '🤔 Did you forget to call the function with ()?',)

        # Validate the arguments.
        if require == True:
            cls.Require(given)
            
        isClass = cls.IsType(given=given, expect=expect)

        if isClass == None or isClass == True:
            return
        
        else:
            import inspect
            tg = type(given)

            try: tgf = inspect.getfile(tg)
            except: tgf = '<built-in>'

            try: originalFile = inspect.getfile(expect)
            except: originalFile = '<built-in>'

            LOG.RaiseValidationException(
                f'📦 AssertIsClass', 
                f'Expected type={expect.__name__}',
                f' from {originalFile}',
                f'but given type=({tg.__name__})',
                f' from {tgf}',
                f' value=', given,
                msg)
            
