from AWS_MOCKS import AWS_MOCKS
from NLWEB import NLWEB
from pollyweb.utils.TESTS import TESTS
from pollyweb.utils.UTILS import UTILS
from AWS import AWS
from MSG import MSG

from pollyweb.utils.LOG import LOG


class AWS_TEST(TESTS):
    '''👉 AWS_TEST is a class for testing AWS components in-memory, without
    making actual AWS calls. Is inherited by NLWEB actors.'''


    ICON = '⛅'
           
 
    @classmethod
    def AWS(cls):
        from AWS import AWS
        return AWS()

    @classmethod
    def NLWEB(cls):
        from NLWEB import NLWEB
        return NLWEB()

    @classmethod
    def MOCKS(cls, domain:str=None):
        if domain !=None:
            cls.SetDomain(domain)
        return AWS_MOCKS()
   
    @classmethod
    def UTILS(cls):
        return UTILS()
    

    @classmethod
    def NewMsg(cls, 
        subject:str, 
        body:any={}, 
        sender:str='sender.com', 
        receiver:str='receiver.com'
    ) -> MSG:
        
        m = MSG.Wrap(
            to= receiver,
            subject= subject,
            body= body
        )
        m.RequireFrom(sender)
        m.Stamp()
        m.Sign(signature='<signarure>', hash='<hash>')
        m.VerifyHeader()
        return m


    @classmethod
    def ResetAWS(cls, domain='*'):
        '''👉 Resets the mockup of all AWS sub components.'''
        
        TESTS.Echo = None
        TESTS.Echos = []

        from TALK_EXEC import TALK_EXEC
        TALK_EXEC.Exec = TALK_EXEC.ExecLogic

        cls.ResetMockedComponents()
        cls.MOCKS().WEB().ResetWebMock()
        
        AWS.APPCONFIG().ResetMock()
        AWS.BUS().ResetMock()
        AWS.LAMBDA().ResetMock()
        AWS.DYNAMO().ResetMock()
        AWS.SECRETS().ResetMock()
        AWS.SSM().ResetMock()

        cls.SetDomain(domain=domain)


    _lastSetDomain:str = None
    @classmethod
    def SetDomain(cls, domain:str):
        '''👉 During in-memory tests, sets the mock AWS to the given domain name.'''

        LOG.Print(cls.SetDomain, f'({domain=}):')
        
        if AWS_TEST._lastSetDomain != domain:
            AWS_TEST._lastSetDomain = domain
            ##LOG.Print(f'AWS_TESTS.SetDomain(domain={domain})')

        if domain == None:
            return

        from APPCONFIG_MOCK import APPCONFIG_MOCK
        APPCONFIG_MOCK.SetMockDomain(domain)

        from EVENTBRIDGE_MOCK import EVENTBRIDGE_MOCK
        EVENTBRIDGE_MOCK.SetMockDomain(domain)

        from LAMBDA_MOCK import LAMBDA_MOCK
        LAMBDA_MOCK.SetMockDomain(domain)

        from DYNAMO_MOCK import DYNAMO_MOCK
        DYNAMO_MOCK.SetMockDomain(domain)
        
        from SECRETS_MOCK import SECRETS_MOCK
        SECRETS_MOCK.SetMockDomain(domain)
        
        from SSM_MOCK import SSM_MOCK
        SSM_MOCK.SetMockDomain(domain)

        # Confirm it's set.
        UTILS.AssertEqual(
            given= NLWEB.CONFIG().RequireDomain(),
            expect= domain)
        
    
    _mockedComponents:list[str] = []

    @classmethod
    def ResetMockedComponents(cls):
        AWS_TEST._mockedComponents = []

    @classmethod
    def MarkDomainAsMocked(cls, domain:str, component:any):
        id = f'{domain}/{component.__name__}'
        AWS_TEST._mockedComponents.append(id)
        
    @classmethod
    def IsDomainMocked(cls, domain:str, component:any):
        id = f'{domain}/{component.__name__}'
        if id in AWS_TEST._mockedComponents:
            ##print(f'  Skipping domain={domain}, component={component.__name__}')
            return True
        else:
            cls.MarkDomainAsMocked(domain, component)
            return False