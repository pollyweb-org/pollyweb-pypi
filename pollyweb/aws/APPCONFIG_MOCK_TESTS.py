from pollyweb.utils.TESTS import TESTS
from APPCONFIG_MOCK import APPCONFIG_MOCK
from pollyweb.utils.LOG import LOG


class APPCONFIG_MOCK_TESTS(APPCONFIG_MOCK):
        

    @classmethod
    def TestGet(cls):

        cls.ResetMock()
        with TESTS.AssertValidation():
            cls.GetValue()

        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')
        with TESTS.AssertValidation():    
            cls.GetValue()

        cls.ResetMock()
        cls.MockValue('any-domain.com', 'dummy')
        with TESTS.AssertValidation():
            cls.GetValue()

        # Happy Path
        cls.ResetMock()
        cls.SetMockDomain('any-domain.com')
        cls.MockValue('any-domain.com', 'dummy')
        TESTS.AssertEqual(cls.GetValue(), 'dummy')


    @classmethod
    def TestAllAppConfig(cls):
        LOG.Print('MOCK_APPCONFIG_TESTS.TestAllAppConfig() ==============================')

        cls.TestGet()
        