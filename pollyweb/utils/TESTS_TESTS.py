from .TESTS import TESTS, ValidationException, AssertException
from .LOG import LOG


class TESTS_TESTS(TESTS):
    '''👉 Testing the Test helper.'''


    @classmethod
    def TestAssert(cls):

        cls._Assert(True)
        cls._Assert(True, title='dummy')
        cls.Asserts([True, True])

        with cls.AssertValidation():
            cls._Assert(False)

        with cls.AssertValidation():
            cls.Asserts([True, False])
        

    @classmethod
    def TestAssertTrue(cls):

        cls.AssertTrue(True)
        cls.AssertTrue([True, True])

        with cls.AssertValidation():
            cls.AssertTrue(False)

        with cls.AssertValidation():
            cls.AssertTrue([True, False])

        


    @classmethod
    def TestAssertFalse(cls):

        cls.AssertFalse(False)
        cls.AssertFalse([False, False])

        with cls.AssertValidation():
            cls.AssertFalse(True)

        with cls.AssertValidation():
            cls.AssertFalse([False, True])


    @classmethod
    def TestAssertEquals(cls):

        cls.AssertEqual(given=1, expect=1)
        cls.AssertEqual(False, False)
        cls.AssertEqual([1], [1])
        cls.AssertEqual({'a':1}, {'a':1})
        cls.AssertEqual(None, None)
        cls.AssertEqual('a', 'a')
        

        cls.AssertEquals([
            [ 1, 1 ],
            [ False, False ],
            [ [1], [1] ],
            [ {'a':1}, {'a':1} ],
            [ None, None ],
            [ 'a', 'a' ]
        ])

        with cls.AssertValidation():
            cls.AssertEqual(1, 2)

        with cls.AssertValidation():
            cls.AssertEqual(False, True)

        with cls.AssertValidation():
            cls.AssertEqual(1, True)

        with cls.AssertValidation():
            cls.AssertEqual(1, {})

        with cls.AssertValidation():
            cls.AssertEqual(1, None)

        with cls.AssertValidation():
            cls.AssertEquals([[ 1, 2 ]])


    @classmethod
    def TestAssertNotEqual(cls):

        cls.AssertNotEqual(given=1, expect=2)
        cls.AssertNotEqual(False, True)
        cls.AssertNotEqual([1], [2])
        cls.AssertNotEqual({'a':1}, {'a':2})
        cls.AssertNotEqual(None, 1)
        cls.AssertNotEqual('a', 'b')

        with cls.AssertValidation():
            cls.AssertNotEqual(1, 1)

        with cls.AssertValidation():
            cls.AssertNotEqual(False, False)

        with cls.AssertValidation():
            cls.AssertNotEqual(True, True)

        with cls.AssertValidation():
            cls.AssertNotEqual({}, {})

        with cls.AssertValidation():
            cls.AssertNotEqual(None, None)

    
    @classmethod
    def TestAssertClass(cls):

        cls.AssertClass(given=1, expected=int)
        cls.AssertClass(given='', expected=str)
        cls.AssertClass(given=True, expected=bool)
        cls.AssertClass(given={'a':1}, expected=dict)
        cls.AssertClass(given=[], expected=list)

        with cls.AssertValidation():
            cls.AssertClass(given=[], expected=str)

        with cls.AssertValidation():
            cls.AssertClass(given=1, expected=bool)

        with cls.AssertValidation():
            cls.AssertClass(given=1, expected=dict)

        with cls.AssertValidation():
            cls.AssertClass(given=1, expected=list)
        

    @classmethod
    def _raiseValidationException(cls):
        LOG.RaiseValidationException()
    

    @classmethod
    def TestAssertValidation(cls):
        # Validation
        with cls.AssertValidation():
            cls._raiseValidationException()

        # Unhappy path for exceptions.
        try:
            with cls.AssertValidation():
                pass
            LOG.RaiseException('An assert exception was expected!')
        except AssertException:
            pass


    @classmethod
    def TestAllTests(cls):
        LOG.Print('TESTS_TESTS.TestAllTests() ==============================')
        
        cls.TestAssertValidation()
        cls.TestAssert()
        cls.TestAssertFalse()
        cls.TestAssertTrue()
        cls.TestAssertEquals()
        cls.TestAssertNotEqual()
        cls.TestAssertClass()
        