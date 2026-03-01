from .TESTS import TESTS
from .UTILS_TYPES import UTILS_TYPES


class UTILS_TYPES_TESTS(UTILS_TYPES):


    @classmethod
    def TestAssertIsClass(cls):

        cls.AssertIsType(given=None, expect=str)
        cls.AssertIsType(given='', expect=str)
        cls.AssertIsType(given=1, expect=int)
        cls.AssertIsType(given=False, expect=bool)
        cls.AssertIsType(given={}, expect=dict)
        cls.AssertIsType(given=[], expect=list)

        with TESTS.AssertValidation():
            cls.AssertIsType(given='', expect=int)

        with TESTS.AssertValidation():
            cls.AssertIsType(given=1, expect=str)

        with TESTS.AssertValidation():
            cls.AssertIsType(given=False, expect=int)

        with TESTS.AssertValidation():
            cls.AssertIsType(given={}, expect=str)

        with TESTS.AssertValidation():
            cls.AssertIsType(given=[], expect=str)


    @classmethod
    def TestIsUuid(cls):
        TESTS.AssertEqual(cls.IsUUID(None), None)
        uuid = cls.UUID()
        TESTS.AssertTrue(cls.IsUUID(uuid), )
        TESTS.AssertFalse(cls.IsUUID("/"+cls.UUID()))
        TESTS.AssertFalse(cls.IsUUID("/"))


    @classmethod
    def TestAssertIsUUID(cls):
        uuid = cls.UUID()
        cls.AssertIsUUID(uuid)

        with TESTS.AssertValidation():
            cls.AssertIsUUID("/"+uuid)
        with TESTS.AssertValidation():
            cls.AssertIsUUID("/")
            

    @classmethod
    def TestIsInt(cls):
        
        TESTS.AssertTrue(cls.IsInt("123"))
        TESTS.AssertFalse(cls.IsInt("123.45"))
        TESTS.AssertFalse(cls.IsInt("abc"))

        TESTS.AssertTrue(cls.IsInt(123))
        TESTS.AssertFalse(cls.IsInt(123.45))
        TESTS.AssertFalse(cls.IsInt([1, 2, 3]))


    @classmethod
    def TestIsFloat(cls):
        
        TESTS.AssertTrue(cls.IsFloat("123"))
        TESTS.AssertTrue(cls.IsFloat("123.45"))
        TESTS.AssertFalse(cls.IsFloat("abc"))

        TESTS.AssertTrue(cls.IsFloat(123))
        TESTS.AssertTrue(cls.IsFloat(123.45))
        TESTS.AssertFalse(cls.IsFloat([1, 2, 3]))


    @classmethod
    def TestRequireInt(cls):
        
        cls.RequireInt("123")
        with TESTS.AssertValidation():
            cls.RequireInt(None)
        with TESTS.AssertValidation():
            cls.RequireInt("123.45")
        with TESTS.AssertValidation():
            cls.RequireInt("abc")

        cls.RequireInt(123)
        with TESTS.AssertValidation():
            cls.RequireInt(123.45)
        with TESTS.AssertValidation():
            cls.RequireInt([1, 2, 3])


    @classmethod
    def TestRequireFloat(cls):
        
        cls.RequireFloat("123")
        cls.RequireFloat("123.45")
        with TESTS.AssertValidation():
            cls.RequireFloat(None)
        with TESTS.AssertValidation():
            cls.RequireFloat("abc")

        cls.RequireFloat(123)
        cls.RequireFloat(123.45)
        with TESTS.AssertValidation():
            cls.RequireFloat([1, 2, 3])


    @classmethod
    def TestRequireString(cls):
        cls.RequireString("abc")
        with TESTS.AssertValidation():
            cls.RequireString(None)
        with TESTS.AssertValidation():
            cls.RequireString(123)
        with TESTS.AssertValidation():
            cls.RequireString([1, 2, 3])



    @classmethod
    def TestIsClass(cls):

        TESTS.AssertEqual(
            given= cls.IsType(given=None, expect=str),
            expect= None)

        TESTS.AssertTrue([
            cls.IsType(given='', expect=str),
            cls.IsType(given=1, expect=int),
            cls.IsType(given=False, expect=bool),
            cls.IsType(given={}, expect=dict),
            cls.IsType(given=[], expect=list)
        ])

        TESTS.AssertFalse([
            cls.IsType(given='', expect=int),
            cls.IsType(given=1, expect=str),
            cls.IsType(given=False, expect=int),
            cls.IsType(given={}, expect=str),
            cls.IsType(given=[], expect=str)
        ])


    @classmethod
    def TestAssertIsString(cls):
        cls.AssertIsStr(None)
        cls.AssertIsStr('')
        cls.AssertIsStr('abc')

        TESTS.AssertEqual(
            cls.AssertIsStr('abc'), 'abc')

        with TESTS.AssertValidation():
            cls.AssertIsStr(123)
        with TESTS.AssertValidation():
            cls.AssertIsStr([1, 2, 3])


    @classmethod
    def TestAllTypes(cls):
        
        cls.TestRequireInt()
        cls.TestRequireFloat()
        cls.TestRequireString()
        
        cls.TestAssertIsClass()
        cls.TestAssertIsUUID()

        cls.TestIsInt()
        cls.TestIsFloat()
        cls.TestIsClass()
        cls.TestIsUuid()


        cls.TestAssertIsString()