
from PW_UTILS.TESTS import TESTS
from SECRETS_MOCK import SECRETS_MOCK
from PW_UTILS.LOG import LOG


class SECRETS_MOCK_TESTS(SECRETS_MOCK):


    @classmethod
    def TestGetSecret(cls):
        
        cls.ResetMock()
        cls.MockValue(domain='any-domain.com', secrets={'A':'1', 'B':'2'})
        with TESTS.AssertValidation():
            cls.GetSecret('A')

        cls.ResetMock()
        cls.SetMockDomain(domain='any-domain.com')
        with TESTS.AssertValidation():
            cls.GetSecret('A')

        cls.ResetMock()
        cls.MockValue(domain='any-domain.com', secrets={'A':'1', 'B':'2'})
        cls.SetMockDomain(domain='any-domain.com')
        with TESTS.AssertValidation():
            cls.GetSecret('C')

        # Happy Path
        cls.ResetMock()
        cls.MockValue(domain='any-domain.com', secrets={'A':'1', 'B':'2'})
        cls.SetMockDomain(domain='any-domain.com')
        TESTS.AssertEqual(cls.GetSecret('A'), '1')
        TESTS.AssertEqual(cls.GetSecret('B'), '2')


    @classmethod
    def TestSetSecret(cls):
        
        cls.ResetMock()
        with TESTS.AssertValidation():
            cls.SetSecret('A','1')

        # Happy Path
        cls.ResetMock()
        cls.SetMockDomain(domain='any-domain.com')
        cls.SetSecret('B','2')
        TESTS.AssertEqual(cls.GetSecret('B'), '2')


    @classmethod
    def TestAllSecrets(cls):
        LOG.Print('MOCK_SECRETS_TESTS.TestAllSecrets() ==============================')
        
        cls.TestGetSecret()
        cls.TestSetSecret()
        