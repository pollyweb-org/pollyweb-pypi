# 📚 UTILS


from .UTILS_OBJECTS import UTILS_OBJECTS
from .TESTS import TESTS
from .STRUCT import STRUCT


class UTILS_OBJECTS_TESTS(
    UTILS_OBJECTS
): 


    @classmethod
    def TestCopy(cls):
        # Normal.
        a={'x':1}
        b=a
        b['x']=2 
        TESTS.AssertEqual(a['x'], 2)

        # Copied.
        a= {'x':1}
        c= cls.Copy(a); 
        c['x']=2 
        TESTS.AssertEqual(a['x'], 1)
    

    @classmethod
    def TestUUID(cls):
        TESTS.AssertTrue(len(cls.UUID()) > 5)
    
    
    @classmethod
    def TestCorrelation(cls):
        TESTS.AssertTrue(len(cls.Correlation()) > 5)


    @classmethod
    def TestCanonicalize(cls):
        TESTS.AssertEqual(
            cls.Canonicalize({'a': 1, 'b': True }),
            '{"a":1,"b":true}'
        )


    @classmethod
    def TestMerge(cls):
        TESTS.AssertEquals([
            [cls.Merge({'a':1}, {'b':2}), {'a':1,'b':2}],
            [cls.Merge({'a':1}, {'a':3, 'b':2}), {'a':3,'b':2}],
            [cls.Merge({'a':1}, None), {'a':1}],
            [cls.Merge(None, {'b':2}), {'b':2}]
        ])
    
   
    @classmethod
    def TestRequireArgs(cls):
        TESTS.AssertEquals([
            [cls.RequireArgs([]), None],
            [cls.RequireArgs([{}, False, 'xpto', 123]), None],
            [cls.RequireArgs([STRUCT("a")]), None],
            [cls.RequireArgs([STRUCT("a"), STRUCT("b")]), None]
        ]) 

        with TESTS.AssertValidation():
            cls.RequireArgs([None])

        with TESTS.AssertValidation():
            cls.RequireArgs(['  '])

        with TESTS.AssertValidation():
            cls.RequireArgs([''])


    @classmethod
    def TestIsNoneOrEmpty(cls):
        
        TESTS.AssertEqual(cls.IsNoneOrEmpty(None), True)
        TESTS.AssertEqual(cls.IsNoneOrEmpty('  '), True)
        TESTS.AssertEqual(cls.IsNoneOrEmpty([]), True)

        TESTS.AssertEqual(cls.IsNoneOrEmpty({}), False)
        TESTS.AssertEqual(cls.IsNoneOrEmpty(False), False)
        TESTS.AssertEqual(cls.IsNoneOrEmpty(123), False)
        TESTS.AssertEqual(cls.IsNoneOrEmpty('xpto'), False)

        '''
        TESTS.AssertEqual(
            cls.IsNoneOrEmpty(STRUCT({})), 
            STRUCT({}).IsMissingOrEmpty())
        '''
        
        TESTS.AssertEqual(
            cls.IsNoneOrEmpty(STRUCT({'a':1})), 
            STRUCT({'a':1}).IsMissingOrEmpty())


    @classmethod
    def TestKeysOfDictionary(cls):
        TESTS.AssertEquals([
            [cls.KeysOfDictionary({'a':1, 'b':2}), ['a','b']],
            [cls.KeysOfDictionary({}), []]
        ])
        
        with TESTS.AssertValidation():
            cls.KeysOfDictionary(None)
        


    @classmethod
    def TestAssertEqual(cls):

        cls.AssertEqual(None, None)
        cls.AssertEqual(None, STRUCT(None))
        cls.AssertEqual(STRUCT(None), None)
        cls.AssertEqual(1, 1)
        cls.AssertEqual(1, 1)
        cls.AssertEqual(True, True)
        cls.AssertEqual('1', '1')
        cls.AssertEqual([1], [1])

        with TESTS.AssertValidation():
            cls.AssertEqual('a', 'b')
        with TESTS.AssertValidation():
            cls.AssertEqual(1, 2)
        with TESTS.AssertValidation():
            cls.AssertEqual([], [1])
        with TESTS.AssertValidation():
            cls.AssertEqual('1', 1)
        

    @classmethod
    def TestAssertInterval(cls):
        cls.AssertInterval(1, 1, 1)
        cls.AssertInterval(1, 0, 2)

        with TESTS.AssertValidation():
            cls.AssertInterval(0, 1, 1)
            
        with TESTS.AssertValidation():            
            cls.AssertInterval(2, 1, 1)
        


    @classmethod
    def TestIsEmoji(cls):
        
        TESTS.AssertTrue(cls.IsEmoji('👉️'))
        TESTS.AssertTrue(cls.IsEmoji('🧪'))
        TESTS.AssertTrue(cls.IsEmoji('🧱'))
        TESTS.AssertTrue(cls.IsEmoji('🐍'))

        TESTS.AssertFalse(cls.IsEmoji('👉️ '))
        TESTS.AssertFalse(cls.IsEmoji('A'))
        TESTS.AssertFalse(cls.IsEmoji(''))
        TESTS.AssertFalse(cls.IsEmoji(None))
        TESTS.AssertFalse(cls.IsEmoji('👉️A'))
        TESTS.AssertFalse(cls.IsEmoji('A👉️'))
        TESTS.AssertFalse(cls.IsEmoji('A👉️A'))

    
    @classmethod
    def TestGetEmojiInName(cls):
        TESTS.AssertEqual(cls.GetEmojiInName('asdasd'), None)
        TESTS.AssertEqual(cls.GetEmojiInName('👉️'), '👉️')
        TESTS.AssertEqual(cls.GetEmojiInName('👉️A'), None)
        TESTS.AssertEqual(cls.GetEmojiInName('👉️ A'), '👉️')
        TESTS.AssertEqual(cls.GetEmojiInName('A👉️'), None)
        TESTS.AssertEqual(cls.GetEmojiInName('A 👉️'), '👉️')
        TESTS.AssertEqual(cls.GetEmojiInName('A👉️A'), None)
        TESTS.AssertEqual(cls.GetEmojiInName('A👉️.txt'), None)
        TESTS.AssertEqual(cls.GetEmojiInName('A 👉️.txt'), None)


    @classmethod
    def TestCamelToUppercase(cls):
        TESTS.AssertEqual(cls.CamelToUppercase(None), None)
        TESTS.AssertEqual(cls.CamelToUppercase(''), '')
        TESTS.AssertEqual(cls.CamelToUppercase('a'), 'A')
        TESTS.AssertEqual(cls.CamelToUppercase('A'), 'A')
        TESTS.AssertEqual(cls.CamelToUppercase('aB'), 'A_B')
        TESTS.AssertEqual(cls.CamelToUppercase('AB'), 'A_B')
        TESTS.AssertEqual(cls.CamelToUppercase('aBC'), 'A_B_C')
        TESTS.AssertEqual(cls.CamelToUppercase('ABC'), 'A_B_C')     
        TESTS.AssertEqual(cls.CamelToUppercase('HelloWorld'), 'HELLO_WORLD')
        TESTS.AssertEqual(cls.CamelToUppercase('HelloWorldAgain'), 'HELLO_WORLD_AGAIN')
        TESTS.AssertEqual(cls.CamelToUppercase('Hello'), 'HELLO')   


    @classmethod
    def TestAllObjects(cls):

        # MATCH
        cls.TestAssertEqual()
        cls.TestAssertInterval()
        
        # REQUIRE
        cls.TestRequireArgs()

        # OTHERS
        cls.TestCopy()   
        cls.TestUUID()
        cls.TestCorrelation()   
        cls.TestCanonicalize()
        cls.TestMerge()
        cls.TestIsNoneOrEmpty()
        cls.TestKeysOfDictionary()
        cls.TestIsEmoji()
        cls.TestGetEmojiInName()

        cls.TestCamelToUppercase()