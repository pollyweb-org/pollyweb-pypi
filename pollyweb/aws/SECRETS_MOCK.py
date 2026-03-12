from LOG import LOG
from LOG import LOG


class SECRETS_MOCK:


    _activeDomain:str = None
    _domains:dict[str,dict[str,str]] = {}


    @classmethod
    def ResetMock(cls):
        SECRETS_MOCK._activeDomain = None
        SECRETS_MOCK._domains = {}


    @classmethod
    def GetSecret(cls, secretId:str):
        
        if not SECRETS_MOCK._activeDomain:
            LOG.RaiseValidationException('Set a domain fist!')
        
        if SECRETS_MOCK._activeDomain not in SECRETS_MOCK._domains:
            LOG.RaiseValidationException(f'Set up the [{SECRETS_MOCK._activeDomain}] domain first!')
        
        if secretId not in SECRETS_MOCK._domains[SECRETS_MOCK._activeDomain]:
            LOG.RaiseValidationException(f'Secret [{secretId}] not found!')

        return SECRETS_MOCK._domains[
            SECRETS_MOCK._activeDomain
        ][secretId]


    @classmethod
    def SetSecret(cls, name:str, value:str):
        
        if SECRETS_MOCK._activeDomain == None:
            LOG.RaiseValidationException('Set a domain fist!')
        
        if SECRETS_MOCK._activeDomain not in SECRETS_MOCK._domains:
            SECRETS_MOCK._domains[SECRETS_MOCK._activeDomain] = {}
        
        SECRETS_MOCK._domains[
            SECRETS_MOCK._activeDomain
        ][name] = value


    @classmethod
    def SetMockDomain(cls, domain:str):
        SECRETS_MOCK._activeDomain = domain


    @classmethod
    def MockValue(cls, domain:str, secrets:dict[str,str]):
        SECRETS_MOCK._domains[domain] = secrets