from NLWEB import NLWEB
from PW_UTILS.TESTS import TESTS
from PW_UTILS.UTILS import UTILS
from AWS import AWS
from MSG import MSG
from LOG import LOG


class AWS_MOCKS:
    '''👉 AWS_MOCKS is a class for testing AWS components in-memory, without
    making actual AWS calls. Is referenced by AWS and AWS_TEST.'''
    

    ICON = '⛅'


    @classmethod
    def ACTOR(cls):
        from ACTOR_MOCKS import ACTOR_MOCKS
        return ACTOR_MOCKS()
    
    @classmethod
    def APPCONFIG(cls):
        from APPCONFIG_MOCK import APPCONFIG_MOCK
        return APPCONFIG_MOCK()
    
    @classmethod
    def BROKER(cls):
        from BROKER_MOCKS import BROKER_MOCKS
        return BROKER_MOCKS()

    @classmethod
    def BUS(cls):
        from EVENTBRIDGE_MOCK import EVENTBRIDGE_MOCK
        return EVENTBRIDGE_MOCK()
    
    @classmethod
    def BUYER(cls):
        from BUYER_MOCKS import BUYER_MOCKS
        return BUYER_MOCKS()
    
    @classmethod
    def COLLECTOR(cls, alias:str=None):
        from COLLECTOR_MOCKS import COLLECTOR_MOCKS
        return COLLECTOR_MOCKS()
    
    @classmethod
    def CONSUMER(cls, alias:str=None):
        from CONSUMER_MOCKS import CONSUMER_MOCKS
        return CONSUMER_MOCKS()
    
    @classmethod
    def DATASET(cls):
        from DATASET_MOCKS import DATASET_MOCKS
        return DATASET_MOCKS()

    @classmethod
    def DYNAMO(cls, alias:str=None):
        from DYNAMO_MOCK import DYNAMO_MOCK
        return DYNAMO_MOCK(alias=alias)
    
    @classmethod
    def EPHEMERAL_BUYER(cls):
        from EPHEMERAL_BUYER_MOCKS import EPHEMERAL_BUYER_MOCKS
        return EPHEMERAL_BUYER_MOCKS()
    
    @classmethod
    def EPHEMERAL_SUPPLIER(cls):
        from EPHEMERAL_SUPPLIER_MOCKS import EPHEMERAL_SUPPLIER_MOCKS
        return EPHEMERAL_SUPPLIER_MOCKS()

    @classmethod
    def GRAPH(cls):
        from GRAPH_MOCKS import GRAPH_MOCKS
        return GRAPH_MOCKS()
    
    @classmethod
    def HANDLER(cls):
        from PW_UTILS.HANDLER_MOCKS import HANDLER_MOCKS
        return HANDLER_MOCKS()

    @classmethod
    def HOST(cls):
        from HOST_MOCKS import HOST_MOCKS
        return HOST_MOCKS()

    @classmethod
    def ISSUER(cls, alias:str=None):
        from ISSUER_MOCKS import ISSUER_MOCKS
        return ISSUER_MOCKS()

    @classmethod
    def LAMBDA(cls):
        from LAMBDA_MOCK import LAMBDA_MOCK
        return LAMBDA_MOCK()
    
    @classmethod
    def LISTENER(cls):
        from LISTENER_MOCKS import LISTENER_MOCKS
        return LISTENER_MOCKS()
    
    @classmethod
    def MANIFEST(cls):
        from MANIFEST_MOCKS import MANIFEST_MOCKS
        return MANIFEST_MOCKS()
    
    @classmethod
    def MANIFESTER(cls):
        from MANIFESTER_MOCKS import MANIFESTER_MOCKS
        return MANIFESTER_MOCKS()

    @classmethod
    def MESSENGER(cls):
        from MESSENGER_MOCKS import MESSENGER_MOCKS
        return MESSENGER_MOCKS()
    
    @classmethod
    def NOTIFIER(cls):
        from NOTIFIER_MOCK import NOTIFIER_MOCK
        return NOTIFIER_MOCK()
    
    @classmethod
    def PAYER(cls):
        from PAYER_MOCKS import PAYER_MOCKS
        return PAYER_MOCKS()
    
    @classmethod
    def PUBLISHER(cls):
        from PUBLISHER_MOCKS import PUBLISHER_MOCKS
        return PUBLISHER_MOCKS()

    @classmethod
    def S3(cls):
        from S3_MOCK import S3_MOCK
        return S3_MOCK()
    
    @classmethod
    def SELFIE_BUYER(cls):
        from SELFIE_BUYER_MOCKS import SELFIE_BUYER_MOCKS
        return SELFIE_BUYER_MOCKS()
    
    @classmethod
    def SELFIE_SUPPLIER(cls):
        from SELFIE_SUPPLIER_MOCKS import SELFIE_SUPPLIER_MOCKS
        return SELFIE_SUPPLIER_MOCKS()
    
    @classmethod
    def SELLER(cls):
        from SELLER_MOCKS import SELLER_MOCKS
        return SELLER_MOCKS()
    
    @classmethod
    def SSM(cls):
        from SSM_MOCK import SSM_MOCK
        return SSM_MOCK()
    
    @classmethod
    def SUBSCRIBER(cls):
        from SUBSCRIBER_MOCKS import SUBSCRIBER_MOCKS
        return SUBSCRIBER_MOCKS()
    
    @classmethod
    def SUPPLIER(cls):
        from SUPPLIER_MOCKS import SUPPLIER_MOCKS
        return SUPPLIER_MOCKS()

    @classmethod 
    def SYNCAPI(cls):
        from SYNCAPI_MOCKS import SYNCAPI_MOCKS
        return SYNCAPI_MOCKS()

    @classmethod
    def TALKER(cls):
        from TALKER_MOCKS import TALKER_MOCKS
        return TALKER_MOCKS()

    @classmethod
    def TRANSCRIBER_BUYER(cls):
        from TRANSCRIBER_BUYER_MOCKS import TRANSCRIBER_BUYER_MOCKS
        return TRANSCRIBER_BUYER_MOCKS()

    @classmethod
    def TRANSCRIBER_SUPPLIER(cls):
        from TRANSCRIBER_SUPPLIER_MOCKS import TRANSCRIBER_SUPPLIER_MOCKS
        return TRANSCRIBER_SUPPLIER_MOCKS()

    @classmethod
    def TRANSFER(cls):
        from TRANSFER_MOCKS import TRANSFER_MOCKS
        return TRANSFER_MOCKS()

    @classmethod
    def VAULT(cls):
        from VAULT_MOCKS import VAULT_MOCKS
        return VAULT_MOCKS()
    
    @classmethod
    def WEB(cls):
        from WEB_MOCK import WEB_MOCK
        return WEB_MOCK()



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
        
        if AWS_TESTS._lastSetDomain != domain:
            AWS_TESTS._lastSetDomain = domain
            ##LOG.Print(f'AWS_TESTS.SetDomain(domain={domain})')

        if domain == None:
            return

        AWS.APPCONFIG().SetMockDomain(domain)
        AWS.BUS().SetMockDomain(domain)
        AWS.LAMBDA().SetMockDomain(domain)
        AWS.DYNAMO().SetMockDomain(domain)
        AWS.SECRETS().SetMockDomain(domain)
        AWS.SSM().SetMockDomain(domain)

        # Confirm it's set.
        UTILS.AssertEqual(
            given= NLWEB.CONFIG().RequireDomain(),
            expect= domain)
        
    
    _mockedComponents:list[str] = []

    @classmethod
    def ResetMockedComponents(cls):
        AWS_TESTS._mockedComponents = []

    @classmethod
    def MarkDomainAsMocked(cls, domain:str, component:any):
        id = f'{domain}/{component.__name__}'
        AWS_TESTS._mockedComponents.append(id)
        
    @classmethod
    def IsDomainMocked(cls, domain:str, component:any):
        id = f'{domain}/{component.__name__}'
        if id in AWS_TESTS._mockedComponents:
            ##print(f'  Skipping domain={domain}, component={component.__name__}')
            return True
        else:
            cls.MarkDomainAsMocked(domain, component)
            return False