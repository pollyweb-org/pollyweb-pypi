from PW_AWS.AWS_TEST import AWS_TEST
from WEB import WEB
from SYNCAPI import SYNCAPI
from pollyweb import STRUCT


class SYNCAPI_MOCKS(SYNCAPI, AWS_TEST):
    

    @classmethod
    def _signerFn(cls, request:any):
        return {
            "hash": "<hash>",
            "signature": "<signature>",
            "isVerified": True
        }
    

    @classmethod
    def _validatorFn(cls, request:any):
        return {
            "hash": "<hash>",
            "isVerified": True
        }


    @classmethod
    def _keyPairGeneratorFn(cls, request:any):
        return {
            'PrivateKey': 'priv',
            'PublicKey': '<pk>'
        }



    @classmethod
    def _mockSyncApiDomain(cls, domain:str):
        '''👉'''

        cls.SetDomain(domain= domain)

        cls.AWS().SSM().Set(name='/NLWEB/Config/DomainName', value=domain)
        cls.AWS().SECRETS().Get('/NLWEB/PrivateKey').SetValue('priv')
        cls.AWS().SECRETS().Get('/NLWEB/PublicKey').SetValue('pub')


    @classmethod
    def _mockSyncApiSender(cls, domain:str):
        '''👉 Prepares the SYNC API to make remote calls.'''

        cls._mockSyncApiDomain(domain= domain)

        cls.AWS().LAMBDA().MockInvoke(
            alias= 'SENDER', 
            handler= cls.SENDER().Handle)
        
        cls.AWS().LAMBDA().MockInvoke(
            alias= 'SIGNER', 
            handler= cls._signerFn)
        

    @classmethod
    def _mockSyncApiDKIM(cls):

        # Ignore the setter, we won't change the DNS durting tests.
        cls.MOCKS().LAMBDA().MockInvoke(
            alias= 'DkimSetterFn')

        # Fake the KeyPair generator, it's in Node!
        cls.MOCKS().LAMBDA().MockInvoke(
            alias= 'GENERATOR',
            handler= cls._keyPairGeneratorFn)

        # Map the rotator directly.
        cls.MOCKS().LAMBDA().MockInvoke(
            alias= 'ROTATOR', 
            handler= cls.DKIM().HandleKeyPairRotator)
        
        # Map the setter directly.
        cls.MOCKS().LAMBDA().MockInvoke(
            alias= 'SecretSetterFn',
            handler= cls.DKIM().HandleSecretSetter)
    

    @classmethod
    def _mockSyncApiReceiver(cls, domain:str):
        '''👉 Prepares the SYNC API to receive messages.'''

        cls._mockSyncApiDomain(domain= domain)

        # The request comes from the internet.
        cls.MOCKS().WEB().MockDomain(
            domain= domain, 
            handler= cls.RECEIVER().Handle)

        # The signature is validated.
        cls.MOCKS().LAMBDA().MockInvoke(
            alias= 'VALIDATOR', 
            handler= cls._validatorFn)


    @classmethod
    def MockSyncApi(cls, domain:str='*'):
        if cls.IsDomainMocked(domain, cls) == True:
            return
        
        cls._mockSyncApiReceiver(domain=domain)
        cls._mockSyncApiSender(domain=domain)
        cls._mockSyncApiDKIM()


    INDEX = 0

    @classmethod
    def MockHandler(cls, 
                    domain:str, 
                    subject:str, 
                    handler:object=AWS_TEST._echo, 
                    ignoreValidation:bool=False
                    ):

        cls.MockSyncApi(domain= domain)
        cls.SetDomain(domain= domain)

        alias = f'Fx-{cls.INDEX}-{subject}'
        cls.INDEX = cls.INDEX+1

        # The MSG is sent to a handler per subject.
        ##LOG.Print(f'SYNCAPI_MOCKS.MockHandler(domain={domain}, subject={subject})')
        cls.NLWEB().BEHAVIORS().SYNCAPI().RECEIVER().MAP().New(
            subject= subject, 
            handler= alias,
            ignoreValidation= ignoreValidation)
        
        # The handler then returns the response (or not).
        cls.MOCKS().LAMBDA().MockInvoke(
            alias= alias,
            handler= handler)
        

    @classmethod
    def MockHandlers(cls, domain:str, ignoreValidation:bool, pairs:dict[str,object]):
        # Add all pairs to the MAP table on SYNCAPI.

        for subject in STRUCT(pairs).Attributes():
            cls.MOCKS().SYNCAPI().MockHandler(
                domain= domain,
                subject= subject,
                handler= pairs[subject],
                ignoreValidation= ignoreValidation
            )


    @classmethod
    def MockReceive(cls, domain:str, event:dict) -> str:
        '''👉 Sends a payload to the domain's inbox.'''

        cls.SetDomain(domain=domain)

        return WEB().HttpPost(
            url= f'https://pollyweb.{domain}/inbox',
            body= event)
    

 