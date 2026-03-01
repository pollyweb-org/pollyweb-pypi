# 📚 UTILS

from typing import List, Dict, Union

from .LOG import LOG


class UTILS_OBJECTS(): 
    '''👉️ Generic methods.'''
    
    ICON= '📦'


    @classmethod
    def Copy(cls, obj:dict):      
        '''👉️ Returns a deep copy of an object, decoupling all object pointers/references.
        * a={x:1}; b=a; b[x]=2 -> a[x] == 2
        * a={x:1}; b=Copy(a); b[x]=2 -> a[x] == 1
        '''  
        from copy import deepcopy
        return deepcopy(obj)
    

    @classmethod
    def UUID(cls):
        ''' 👉️ Generates a new Global Unique Identifier.
        * https://stackoverflow.com/questions/37049289/how-do-i-convert-a-python-uuid-into-a-string '''
        import uuid
        return str(uuid.uuid4())
    
    
    @classmethod
    def Correlation(cls):
        ''' 👉️ Generates a new Global Unique Identifier for a request.
        Docs: https://quip.com/NiUhAQKbj7zi#temp:C:XAYf6d35adc1f4e4f0795954ef86 '''
        correlation = cls.UUID()
        ##LOG.Print(f'{correlation=}')
        return correlation


    @classmethod
    def Canonicalize(cls, object: any) -> str:
        ''' 👉️ Removes the spaces from a string.
        * Source: https://bobbyhadz.com/blog/python-json-dumps-no-spaces 
        * Canonicalize({ a: 1, b: 2 }) -> '{a:1,b:2}'
        '''
        import json
        canonicalized = json.dumps(
            obj= object, 
            separators=(',', ':'))
        
        ##LOG.Print(f'{canonicalized=}')
        return canonicalized

    
    @classmethod
    def Merge(cls, obj1:dict, obj2:dict):
        ''' 👉️ Merges the attributes of a second object into the first.
        Source: https://stackoverflow.com/questions/14839528/merge-two-objects-in-python 
        
        Usage: 
        * Merge({a:1}, {b:2}) -> {a:1,b:2}
        * Merge({a:1}, {a:3, b:2}) -> {a:3,b:2}
        * Merge({a:1}, None) -> {a:1}
        * Merge(None, {b:2}) -> {b:2}
        '''
        
        if obj1 == None:
            return obj2
        if obj2 == None:
            return obj1
        obj1.update(obj2)
        return obj1
    

    @classmethod
    def Require(cls, arg:any, msg:str=None):
        '''👉️ Verifies if a given argument is not empty.'''
        
        if cls.IsNoneOrEmpty(arg):

            reason = ''
            if arg == None:
                reason = f'arg == None'
            elif isinstance(arg, str):
                reason = 'empty string'                
            elif isinstance(arg, list):
                reason = 'empty list'
                
            LOG.RaiseValidationException(
                f'📦 Require: Mandatory argument is empty!',
                f'{reason=}', f'{arg=}', f'{msg=}')

   
    @classmethod
    def RequireArgs(cls, args:Union[List[any],any]):
        '''👉️ Verifies if all given arguments are not empty.

        Valid:
        * RequireArgs([]) -> OK
        * RequireArgs([{}, False, 'xpto', 123]) -> OK
        
        Inherit:
        * RequireArgs([$a]) -> $a.Required()
        * RequireArgs([$a, $b]) -> $a.Required() and $b.Required()

        Exceptions:
        * RequireArgs([None]) -> Exception, null object!
        * RequireArgs(['  ']) -> Exception, empty string!
        * RequireArgs([[]]) -> Exception, empty list!
        '''

        if not isinstance(args, list):
            args = [args]
        
        index = 0
        for arg in args:
            if cls.IsNoneOrEmpty(arg):
                LOG.RaiseValidationException(
                    f'📦 RequireArgs: Mandatory argument is empty: '\
                    f'index={index}, type={type(arg).__name__}, value=({arg})')
            index = index + 1


    @classmethod    
    def IsNoneOrEmpty(cls, arg:any):
        '''👉️ Verifies if a given arguments is empty.

        True (empty)
        * IsNoneOrEmpty(None) -> True
        * IsNoneOrEmpty('  ') -> True (string)
        * IsNoneOrEmpty([]) -> True (list)

        False (non-empty):
        * IsNoneOrEmpty({}) -> False
        * IsNoneOrEmpty(False) -> False
        * IsNoneOrEmpty(123) -> False
        * IsNoneOrEmpty('xpto') -> False
        '''
        LOG.Print(cls.IsNoneOrEmpty, type(arg).__name__)

        # Generic argument.
        if arg == None:
            LOG.Print(cls.IsNoneOrEmpty, f': arg == None -> True')
            return True

        # Struct argument.
        from .STRUCT import STRUCT
        if isinstance(arg, STRUCT):
            return arg.IsMissingOrEmpty()
            
        # String argument.
        if isinstance(arg, str):
            if arg == '' or arg.strip() == '':
                LOG.Print(cls.IsNoneOrEmpty, f': empty string -> True')
                return True
            
        # List argument.
        if isinstance(arg, list):
            if len(arg) == 0:
                LOG.Print(cls.IsNoneOrEmpty, f': empty list -> True')
                return True
            
        LOG.Print(cls.IsNoneOrEmpty, f': otherwise -> False')
        return False


    @classmethod
    def KeysOfDictionary(cls, dictionary:Dict[str, str]):
        '''👉️ Return a list of keys from the dictionary.
        * Source: https://www.geeksforgeeks.org/python-get-dictionary-keys-as-a-list/

        Usage:
        * KeysOfDictionary({a:1, b:2}) -> [a,b]
        * KeysOfDictionary({}) -> []
        * KeysOfDictionary(None) -> Exception!
        '''
        if (dictionary == None):
            LOG.RaiseValidationException('📦 KeysOfDictionary: empty object!')
        return list(dictionary.keys())
       

    @classmethod
    def AssertEqual(cls, given:any, expect:any, msg:Union[str,list]=None):
        
        from .STRUCT import STRUCT
        if expect == STRUCT(None) and given == None: return
        if expect == None and given == STRUCT(None): return
        
        if expect != given:
            from .PRINTABLE_DICT import PRINTABLE_DICT
            LOG.RaiseValidationException(
                '📦 UTILS.Match:', PRINTABLE_DICT(
                    Expected= expect, 
                    Received= given, 
                    ExpectedLen= len(str(expect)), 
                    ReceivedLen= len(str(given)),
                    Message= msg))
        

    @classmethod
    def AssertInterval(cls, value:Union[int,float], lower:Union[int,float], upper:Union[int,float], msg:str=None):
        '''👉️ Checks if a value is in a given interval, or raises an exception.
        * MatchInterval(2,1,5) -> OK
        * MatchInterval(0,1,5) -> Exception
        * MatchInterval(6,1,5) -> Exception
        '''
         
        if value < lower or value > upper:
            LOG.RaiseValidationException(
                f'📦 MatchInternal: Value={value} should be between [{lower}] and [{upper}]!', msg)
        

    @classmethod
    def Raw(cls, obj:any) -> any:
        ''' 👉 Returns a json dumps+loads to remove any internal structs. '''
        if type(obj) in [str,int,bool,float]:
            return obj
        
        # lst, dict, object
        import json
        dumps = json.dumps(obj)
        return json.loads(dumps)
    

    @classmethod
    def Random(cls, min:int, max:int) -> int:
        ''' 👉 Returns a random number between min and max. '''
        import random
        return random.randint(min, max)
    

    @classmethod
    def Default(cls, value:any, default:any) -> any:
        ''' 👉 Returns the value, or a default if empty. '''
        if cls.IsNoneOrEmpty(value): 
            return default
        return value
    

    @classmethod
    def IsEmoji(cls, txt:str):
        '''👉️ Checks if a character is an emoji.
        Example usage
         * IsEmoji('😊') -> True
         * IsEmoji('A') -> False
        '''

        if not txt:
            return False

        # Check if the lenght is between 1 and 2.
        if len(txt) < 1 or len(txt) > 2:
            return False

        # Unicode ranges for emojis
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x1F700, 0x1F77F),  # Alchemical Symbols
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0x2B50, 0x2BFF),    # Additional Miscellaneous Symbols and Pictographs
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
            (0x1F780, 0x1F7FF),  # Geometric Shapes Extended
            (0x1F800, 0x1F8FF),  # Supplemental Arrows-C
        ]
        
        # Check each character in the string
        for char in txt:
            code_point = ord(char)
            for start, end in emoji_ranges:
                if start <= code_point <= end:
                    return True
            
        #LOG.Print(f'📦 UTILS_OBJECTS.IsEmoji: Not an emoji: {txt}.')
        return False


    @classmethod
    def GetEmojiInName(cls, name:str):
        '''👉️ Returns the emoji from a name.
        
        Example:
        * Anything -> None
        * 🧱 Starting -> 🧱
        * Ending 🐍 -> 🐍
        * Between 🧪 Words -> None
        '''

        # Return empty if the name is empty.
        if len(str(name).strip()) == 0:
            return None
        
        # Break into parts by space.
        parts = name.strip().split(' ')
        
        # Check the 1st character.
        if UTILS_OBJECTS.IsEmoji(parts[0].strip()):
            return parts[0].strip()
        
        # Check the last character.
        if UTILS_OBJECTS.IsEmoji(parts[-1].strip()):
            return parts[-1].strip()

        # return empty
        return None
    

    @classmethod
    def LimitLines(cls, text:str, maxLines:int):
        '''👉️ Limits the number of lines in a text.
        * LimitLines('a\nb\nc', 2) -> 'a\nb'
        * LimitLines('a\nb\nc', 3) -> 'a\nb\nc'
        * LimitLines('a\nb\nc', 4) -> 'a\nb\nc'
        '''
        if not maxLines:
            return text
        lines = text.split('\n')
        
        if len(lines) > maxLines:
            ret = '\n'.join(lines[:maxLines]) 
            ret += '\n' 
            # add as many left spaces as the ones in the previous line.
            for i in range(len(lines[maxLines-1])):
                if lines[maxLines-1][i] == ' ':
                    ret += ' '
            ret += '(...)'
            return ret
        
        return text
    

    @classmethod
    def ToProperCase(cls, text:str):
        '''👉️ Converts a string to Proper Case.
        * ToProperCase('hello world') -> 'Hello World'
        * ToProperCase('HELLO WORLD') -> 'Hello World'
        * ToProperCase('Hello World') -> 'Hello World'
        * ToProperCase('helloWorld') -> 'Hello World'
        * ToProperCase('HelloWorld') -> 'Hello World'
        '''
        if not text:
            return text
        return ' '.join([
            word.capitalize() 
            for word in text.split(' ')
        ])


    def CamelToUppercase(word):
        '''👉️ Converts a camel case word to uppercase.
         * addis underscores between words.
        
        Examples:
         * .CamelToUppercase('helloWorld') -> HELLO_WORLD
         * .CamelToUppercase('HelloWorldAgain') -> HELLO_WORLD_AGAIN
         * .CamelToUppercase('Hello') -> HELLO
         * .CamelToUppercase('') -> ''
         * .CamelToUppercase('None') -> None
        '''

        if word == None:
            return None
        
        if len(word) == 0:
            return ''

        result = []

        for char in word:
            if char.isupper():
                result.append('_' + char)
            else:
                result.append(char)

        ret = ''.join(result).upper()

        # Remove any leading underscore.
        if ret[0] == '_':
            ret = ret[1:]

        return ret