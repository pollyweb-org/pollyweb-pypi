# 📚 TESTS

from typing import Union
import json


class ValidationException(Exception):
    '''👉 Exception for unit testing.'''
    pass

class AssertException(Exception):
    pass


class RAWABLE:
    def Raw(self):
        from .LOG import LOG
        LOG.RaiseException('Implement!')
    


class TEST_EXCEPTION:
    '''👉 Expects a ValidationException to be raised, otherwise fails.
    * Usage: with TEST_EXCEPTION():
    '''


    def __init__(self, check:str=None, type:type=None):
        ##LOG.Print('TEST_EXCEPTION.__init__')
        self._check = check
        self._type = type
     

    def __enter__(self):
        ##LOG.Print('TEST_EXCEPTION.__enter__')
        return self
    
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        * https://stackoverflow.com/questions/62086216/is-exit-method-called-when-theres-an-exception-inside-context-manager
        '''
        from .LOG import LOG
        LOG.Print('🧪 TESTS.TEST_EXCEPTION.__exit__')
        
        from .WEB_BASE import UrlNotFoundException

        if exc_type == None:
            ##LOG.Print('An exception should have been raised!')
            LOG.RaiseAssertException(
                f'An exception should have been raised!'
                f' Ckeck={self._check}')
        
        if self._type == None:
            if exc_type in [UrlNotFoundException, ValidationException, AssertException, TypeError]:
                ##LOG.Print('A ValidationException was raised, nice!\n')
                return True
        
        if self._type != None:
            if exc_type == self._type:
                ##LOG.Print('The expected exception was raised, nice!\n')
                return True
        
        ##LOG.Print('Unexpected non-ValidationException!')
        LOG.Print(
            f'Unexpected non-ValidationException:', dict(
                ExpectedType= self._type,
                RaisedType= exc_type, 
                RaisedVal= exc_val, 
                RaisedTB= exc_tb,
                Ckeck= self._check))
        
        raise exc_val



class TESTS:
    '''👉 Test helper.'''


    @classmethod
    def LOG(cls):
        '''👉 Returns the LOG class.'''
        from .LOG import LOG
        return LOG


    @classmethod
    def _Assert(cls, condition:bool, title:str=None, index:int=None):
        '''👉 Tests if a condition is true.
        * Usage: .Assert(condition)
        '''
        ##LOG.Print(f'\nAssert(condition={condition}, title={title})')

        if condition == None:
            cls.LOG().RaiseAssertException('Condition cannot be None!')
        
        elif condition != True:
            cls.LOG().RaiseAssertException(
                f'Condition not met!'
                f'\n Index={index}, '
                f'\n Title=({title}).')
        
        ##LOG.Print('')
        

    @classmethod
    def Asserts(cls, conditions:list[bool]):
        '''👉 Tests if a list of conditions are true.
        * Usage: .Asserts([condition1,condition2])
        '''
        ##LOG.Print(f'\nAsserts(conditions={conditions})')

        index = 0
        for condition in conditions:
            cls._Assert(condition, index=index)
            index = index+1

        ##LOG.Print('')


    @classmethod
    def _isClass(cls, given:any, expect:type) -> Union[None,bool]:
        '''👉️ Checks if the the given value is of a class.
        * IsClass(None, X) -> None
        * IsClass(False, bool) -> True
        * IsClass(False, int) -> False
        * IsClass({}, dict) -> True
        * IsClass(STRUCT({}), dict) -> True
        '''
        ##LOG.Print(f'\nTESTS._isClass(given={type(given).__name__}:{given}, expect={type(expect).__name__}:{expect})')

        if isinstance(given, type):
            cls.LOG().RaiseException(f'Give a value, not a class! Given={given}')

        # Don't check nulls.
        if given == None:
            ##LOG.Print(f'  TESTS._isClass() -> None')
            return None
        
        if isinstance(given, bool) or isinstance(given, int):
            # For native types, compare the type exactly to avoid True==1.
            ##LOG.Print(f'  TESTS._isClass() -> {(type(given) == expect)=}')
            return type(given) == expect
            
        else:
            # For others, allow inheritance.
            ##LOG.Print(f'  TESTS._isClass() -> {isinstance(given, expect)=} or...')
            ##LOG.Print(f'  TESTS._isClass() -> {issubclass(type(given), expect)=}')
            return isinstance(given, expect) or issubclass(type(given), expect)



    @classmethod
    def AssertEqual(cls, given:any, expect:any, msg:str=None):
        '''👉 Tests if two values are equals.
        * Usage: .AssertEqual(given,expected)
        '''
        ##LOG.Print(f'\nAssertEqual(given={given}, expected={expect})')

        from .UTILS import UTILS
        oriGiven = UTILS.Copy(given)
        oriExpect = UTILS.Copy(expect)

        if isinstance(given, type):
            cls.LOG().RaiseException(f'For types, use AssertClass(). Given={given}')
        
        if isinstance(expect, type):
            cls.LOG().RaiseException(f'For types, use AssertClass(). Expect={expect}')

        # VALIDATION --------------------

        equals = False
        
        if isinstance(given, RAWABLE) or issubclass(type(given), RAWABLE):
            #LOG.Print(f'TESTS.AssertEqual(): given.Raw()={given.Raw()}')
            given = given.Raw()

        if isinstance(expect, RAWABLE) or issubclass(type(expect), RAWABLE):
            #LOG.Print(f'TESTS.AssertEqual(): expect.Raw()={expect.Raw()}')
            expect = expect.Raw()

        if False:
            pass
        
        #elif cls._isClass(given, dict) and cls._isClass(expect, dict):
        #    c1 = json.loads(json.dumps(given))
        #    c2 = json.loads(json.dumps(expect))
        #    equals = (c1 == c2)
        
        elif cls._isClass(given, dict) and cls._isClass(expect, dict):
            c1 = given
            c2 = expect
            equals = (c1 == c2)

        else:
            c1 = str(given)
            c2 = str(expect)
            equals = (c1 == c2)

        # EXECUTION --------------------

        if equals:
            ##LOG.Print('Values are the same, ignoring...\n')
            pass
    
        else:
            ##LOG.Print('Values are different, raising exception...\n')
            
            givenType = type(given).__name__
            expectType = type(expect).__name__

            if isinstance(given, dict):
                given = json.dumps(given, indent= 2)

            if isinstance(expect, dict):
                expect = json.dumps(expect, indent= 2)

            ##LOG.Print(f'TESTS.AssertEqual(): given={type(given).__name__}:{given}')
            ##LOG.Print(f'TESTS.AssertEqual(): expect={type(expect).__name__}{expect}')
            ##LOG.Print(f'TESTS.AssertEqual(): c1={type(c1).__name__}:{c1}')
            ##LOG.Print(f'TESTS.AssertEqual(): c2={type(c2).__name__}{c2}')
            ##LOG.Print(f'TESTS.AssertEqual(): {cls._isClass(given, dict)=}')
            ##LOG.Print(f'TESTS.AssertEqual(): {cls._isClass(expect, dict)=}')

            cls.LOG().RaiseAssertException('Value not equal!',
                f'{msg=}', 
                f'given=', oriGiven,
                f'expect=', oriExpect)
        

    @classmethod
    def AssertNotNone(cls, given:any, msg:str=None):
        '''👉 Tests if a value is not none.'''
        if given == None:
            cls.LOG().RaiseAssertException(
                msg or f'Value should not be None!')
            

    @classmethod
    def AssertNone(cls, given:any, msg:str=None):
        '''👉 Tests if a value is not none.'''
        if given != None:
            cls.LOG().RaiseAssertException(
                msg or f'Value should be None!')
        

    @classmethod
    def AssertNotEmpty(cls, given:any, msg:str=None):
        '''👉 Tests if a value is not an empty list.'''
        from .UTILS import UTILS
        UTILS.AssertIsAnyType(given, [list], require=True, msg= msg)
        UTILS.Require(given, msg= msg)


    @classmethod
    def AssertEmpty(cls, given:any, msg:str=None):
        '''👉 Tests if a value is empty.'''
        from .UTILS import UTILS
        UTILS.AssertIsAnyType(given, [list], msg= msg)
        if len(given) != 0:
            cls.LOG().RaiseAssertException(msg or f'List should be empty!')


    @classmethod
    def AssertNotEqual(cls, given:any, expect:any, msg=None):
        '''👉 Tests if two values are not equals.
        * Usage: .AssertNotEqual(given,expected)
        '''
        ##LOG.Print(f'\nAssertNotEqual(given={given}, expected={expected})')

        if str(given) == str(expect):
            ##LOG.Print('Values are equal, raising exception...\n')
            cls.LOG().RaiseAssertException(
                f'NotEqual: not expected=`{expect}`, given=`{given}`!', dict(
                    Given= given,
                    Expect= expect,
                    Message= msg
                ))
        
        else:
            ##LOG.Print('Values are not the same, ignoring...\n')
            pass


    @classmethod
    def AssertJson(cls, given:any, expected:any):
        '''👉 Tests if two values have the same json.'''
        ##LOG.Print(f'\nAssertJson(given={given}, expected={expected})')

        if json.dumps(given) != json.dumps(expected):
            ##LOG.Print('Jsons are different, raising exception...\n')
            cls.LOG().RaiseAssertException(f'Json not equal:\n given=`{given}`,\n expected=`{expected}`!')
        
        else:
            ##LOG.Print('Jsons are the same, ignoring...\n')
            pass


    @classmethod
    def AssertEquals(cls, pairs:list[list]):
        '''👉 Tests if pairs are equals.
        * Usage: .AssertEquals([ [given1,expected1], [given2,expected2] ])
        '''
        ##LOG.Print(f'\nAssertEquals(pairs={pairs})')

        index = 0
        for pair in pairs:

            cls.AssertEqual(
                given=pair[0], 
                expect=pair[1], 
                msg=f'AssertEquals[{index}]')
            
            index = index+1

        ##LOG.Print('')



    @classmethod
    def AssertContainsStr(cls, 
        given:str, 
        expected:str,
        msg:str=None
    ):
        '''👉 Tests if a string contains another string.'''
        
        from .UTILS import UTILS
        UTILS.AssertStrings([given, expected])

        if expected not in given:
            given_oneline = given.replace("\n", "\\n")
            cls.LOG().RaiseAssertException(
                f'Expected string not found in given string!',
                f'Msg= `{msg}`',
                f'Given= `{given_oneline}`',
                f'Expected= `{expected}`')



    @classmethod
    def AssertTrue(cls, 
        conditions:Union[bool,list[bool]], 
        msg:str=None
    ):
        '''👉 Tests if a condition is true.'''
        
        ##LOG.Print(f'\nAssertTrue(conditions={conditions})')

        from .UTILS import UTILS
        UTILS.AssertIsAnyType(conditions, [bool, list], require=True)

        if type(conditions) == bool:
            conditions = [conditions]

        for condition in conditions:
            cls._Assert(condition, title=msg)

        ##LOG.Print('')


    @classmethod
    def AssertFalse(cls, 
        conditions:Union[bool,list[bool]], 
        title:str=None
    ):
        '''👉 Tests if a condition is false.'''

        ##LOG.Print(f'\nAssertFalse(conditions={conditions})')

        if type(conditions) == bool:
            conditions = [conditions]

        for condition in conditions:
            cls._Assert(not condition, title=title)
            
        ##LOG.Print('')


    @classmethod
    def AssertClass(cls, given:any, expected:type):
        '''👉 Tests if a values is from a given class.'''
        ##LOG.Print(f'\nAssertClass(given={given}, expected={expected})')

        if type(given) != expected:
            ##LOG.Print('Classes are different, raising exception...\n')
            cls.LOG().RaiseAssertException(f'Class not equal:\n given=`{type(given)}`, \nexpected=`{expected}`!')
        
        else:
            ##LOG.Print('Classes are the same, ignoring...\n')
            pass

        
    @classmethod
    def AssertValidation(cls, 
        check:str= None,
        type:type= None
    ):
        '''👉 Expects a ValidationException to be raised, otherwise fails.
        * Usage: with .AssertValidation():...'''
        from .LOG import LOG
        LOG.Print(f'🧪 TESTS.AssertValidation()')

        return TEST_EXCEPTION(
            check= check, 
            type= type)
    

    @classmethod
    def AssertIsUUID(cls, value:str):
        size = len('17880417-f90c-44e1-a3f0-772441530dca')
        if value == None:
            cls.LOG().RaiseValidationException(f'Value should be a UUID, but is empty (None)!')
        elif len(value) != size:
            cls.LOG().RaiseValidationException(f'Value=({value}) is not a UUID: size missmatch!')
        elif '-' not in value:
            cls.LOG().RaiseValidationException(f'Value=({value}) is not a UUID: missing daches!')


    Echo = ''
    '''👉 Echo from last message sent.'''

    Echos:list[str] = []
    '''👉 Echo from last message sent.'''


    @staticmethod
    def _echo(event):
        '''👉 Default echo from MockSyncApiSender and MockMessengerSender.'''
        TESTS.Echo = event
        TESTS.Echos.append(event)
        return event
    
