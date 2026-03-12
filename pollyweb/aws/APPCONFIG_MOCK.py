from LOG import LOG
from PW_UTILS.UTILS import UTILS
from LOG import LOG


class APPCONFIG_MOCK():
        

    _activeDomain:str = None
    _domains:dict[str,str] = {}


    @classmethod
    def ResetMock(cls):
        APPCONFIG_MOCK._activeDomain = None
        APPCONFIG_MOCK._domains = {}


    @classmethod
    def GetValue(
        cls,    
        CONFIG_APP: str = 'CONFIG_APP', 
        CONFIG_ENV: str = 'CONFIG_ENV', 
        CONFIG_PROFILE: str = 'CONFIG_PROFILE'
    ) -> str:
        if not APPCONFIG_MOCK._activeDomain:
            LOG.RaiseValidationException('Set a domain first!')
        
        if APPCONFIG_MOCK._activeDomain not in APPCONFIG_MOCK._domains:
            '''
            from MANIFEST_MOCKS import MANIFEST_MOCKS
            domain = MOCK_APPCONFIG._activeDomain
            domains = MOCK_APPCONFIG._domains
            domains[domain] = MANIFEST_MOCKS.MockManifest(domain=domain)
            '''
            LOG.RaiseValidationException(f'First, define AppConfig for domain=({APPCONFIG_MOCK._activeDomain})!')
        
        ret = APPCONFIG_MOCK._domains[
            APPCONFIG_MOCK._activeDomain
        ]
        return ret


    @classmethod
    def SetMockDomain(cls, domain:str):
        '''👉 During in-memory tests, sets the mock AppConfig to the given domain.'''
        APPCONFIG_MOCK._activeDomain = domain


    @classmethod
    def MockValue(cls, domain:str, value:str):
        UTILS.RequireArgs([domain, value])
        UTILS.AssertIsType(value, str)

        APPCONFIG_MOCK._domains[domain] = value