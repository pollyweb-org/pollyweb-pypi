from PW_UTILS.TESTS import TESTS
from SSM_MOCK import SSM_MOCK
from PW_UTILS.LOG import LOG


class SSM_MOCK_TESTS(SSM_MOCK):

    
    @classmethod
    def TestGet(cls):

        cls.ResetMock()
        cls.MockSettings(
            domain= 'any-domain.com', 
            config={ 'A':'1', 'B':'2' })
        with TESTS.AssertValidation():
            cls.Get('A')

        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')
        with TESTS.AssertValidation():
            cls.Get('A')

        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')
        cls.MockSettings(
            domain= 'any-domain.com', 
            config={ 'A':'1', 'B':'2' })
        cls.Get('A')
        with TESTS.AssertValidation():
            cls.Get('C')

        # Happy Path
        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')
        cls.MockSettings(
            domain= 'any-domain.com', 
            config= { 'A':'1', 'B':'2' })
        TESTS.AssertEqual(cls.Get('A'), '1')
        TESTS.AssertEqual(cls.Get('B'), '2')

    
    @classmethod
    def TestSet(cls):

        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')

        cls.Set(name='D', value='4')
        TESTS.AssertEqual(cls.Get('D'), '4')

        cls.Set(name='D', value='5')
        TESTS.AssertEqual(cls.Get('D'), '5')


    @classmethod
    def TestDelete(cls):

        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')
        
        key = 'A'
        cls.Set(name=key, value='4')
        TESTS.AssertEqual(cls.Get(key), '4')

        cls.Delete(key)
        with TESTS.AssertValidation():
            cls.Get(key)


    @classmethod
    def TestAllSettings(cls):
        LOG.Print('MOCK_SSM_TESTS.TestAllSettings() ==============================')
        
        cls.TestGet()
        cls.TestSet()
        cls.TestDelete()
