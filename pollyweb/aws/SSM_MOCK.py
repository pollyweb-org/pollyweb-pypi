from pollyweb.utils.LOG import LOG
from pollyweb.utils.UTILS import UTILS
from pollyweb.utils.LOG import LOG


from SSM_BASE import SSM_BASE
class SSM_MOCK(SSM_BASE):


    @classmethod
    def _VerifyName(cls, name:str):
        
        # Values used in tests.
        if name in ['A', 'B', 'C', 'D']:
            return
        
        # All others must have the /NLWEB/Config/
        if not name.startswith('/NLWEB/Config/'):
            LOG.RaiseValidationException(
                f'Add /NLWEB/Config/ to the config!', f'{name=}')


    _activeDomain:str = None
    _domains:dict[str,dict[str,str]] = {}


    @classmethod
    def ResetMock(cls):
        SSM_MOCK._activeDomain = None
        SSM_MOCK._domains = {}


    @classmethod
    def SetMockDomain(cls, domain:str):
        '''Set the active domain during tests.'''
        if domain not in SSM_MOCK._domains:
            SSM_MOCK._domains[domain] = {}

        SSM_MOCK._activeDomain = domain


    # ✅ DONE
    @classmethod
    def MockSettings(cls, domain:str, config:dict[str, str]):
        if domain not in SSM_MOCK._domains:
            SSM_MOCK._domains[domain] = {}

        # Convert the mocked names.
        config2 = {}
        for name in config:
            if name not in ['A','B','C','D'] and 'NLWEB' not in name.upper():
                name2 = f'/NLWEB/Config/{name}'
            else:
                name2 = name
            config2[name2] = config[name]
            
        # Convert the conversation.
        for name in config2:
            cls._VerifyName(name)
        
        SSM_MOCK._domains[domain].update(config2)


    @classmethod
    def MockGraphSetting(cls, domain:str, graph:str):
        cls.MockSettings(
            domain= domain, 
            config= {
                'Graph': graph
            })
        
    @classmethod
    def MockBrokerSetting(cls, domain:str, broker:str):
        cls.MockSettings(
            domain= domain, 
            config= {
                'Broker': broker
            })
        
    @classmethod
    def MockSelfieSetting(cls, domain:str, selfie:str):
        cls.MockSettings(
            domain= domain, 
            config= {
                'Selfie': selfie
            })
        
    
    @classmethod
    def MockTranscriberSetting(cls, domain:str, transcriber:str):
        cls.MockSettings(
            domain= domain, 
            config= {
                'Transcriber': transcriber
            })
        

    @classmethod
    def MockListenerSetting(cls, domain:str, listener:str):
        cls.MockSettings(
            domain= domain, 
            config= {
                'Listener': listener
            })
        
    
    @classmethod
    def Get(cls, 
        name:str, 
        optional:bool= False,
        region:str= None # Not used in Mock.
    ) -> str:
        
        LOG.Print(f'⛅ SSM.MOCK.Get({name=})',
            f'activeDomain={SSM_MOCK._activeDomain}')

        if not SSM_MOCK._activeDomain:
            if optional:
                return None
            LOG.RaiseValidationException('Set a domain fist!')
        
        if SSM_MOCK._activeDomain not in SSM_MOCK._domains:
            if optional:
                return None
            LOG.RaiseValidationException(
                f'Set up the [{SSM_MOCK._activeDomain}] domain first!')

        LOG.Print(f'⛅ SSM.MOCK.Get({name=}):', 
            'options=', SSM_MOCK._domains[SSM_MOCK._activeDomain])

        cls._VerifyName(name)

        key = name

        if key not in SSM_MOCK._domains[SSM_MOCK._activeDomain]:
            
            if optional:
                LOG.Print(f'⛅ SSM.MOCK.Get({name=}): return None')
                return None
            
            if key == '/NLWEB/Config/DomainName':
                # Return the active domain.
                return SSM_MOCK._activeDomain
            
            if SSM_MOCK._activeDomain == '*':
                LOG.Print(f'⛅ SSM.MOCK.Get({name=}): Ignore if it is a test.')
                return
            
            LOG.RaiseValidationException(
                f'First, setup the SSM Key [{key}] ',
                f'for domain [{SSM_MOCK._activeDomain}]',
                f'Root=', cls._domains)

        ret = SSM_MOCK._domains[SSM_MOCK._activeDomain][key]
        LOG.Print(f'⛅ SSM.MOCK.Get({name=}): return=', ret)
        return ret

    
    @classmethod
    def Set(cls, 
        name: str, 
        value: str, 
        region:str= None # Not used in Mock.
    ):
        UTILS.RequireArgs([name,value])

        cls._VerifyName(name)

        key = name

        SSM_MOCK._domains[SSM_MOCK._activeDomain][key] = value


    @classmethod
    def Delete(cls, 
        name: str, 
        region:str= None # Not used in Mock.
    ):
        
        key = name

        del SSM_MOCK._domains[SSM_MOCK._activeDomain][key]

    