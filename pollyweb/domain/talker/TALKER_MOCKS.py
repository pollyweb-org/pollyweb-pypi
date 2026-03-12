
from PW_AWS.AWS_TEST import AWS_TEST
from NLWEB import NLWEB
from pollyweb import LOG
from TALKER import TALKER


class TALKER_MOCKS(TALKER, AWS_TEST):
    

    @classmethod
    def MockTalker(cls, domain:str, clean:bool=False):
        LOG.Print(' TALKER.MOCKS.MockTalker()', f'{domain=}')

        if cls.IsDomainMocked(domain=domain, component=cls):
            return 
        
        cls.MockTalkerSuppliers(domain=domain, clean=clean)
    
        
    @classmethod
    def MockTalkerSuppliers(cls, domain:str, clean:bool=False):

        cls.MOCKS().BUYER().MockBuyer(buyer=domain, clean=clean)

        # Register suppliers.
        cls.MOCKS().SELFIE_BUYER().RegisterHandlers(domain)
        cls.MOCKS().EPHEMERAL_BUYER().RegisterHandlers(domain)
        cls.MOCKS().TRANSCRIBER_BUYER().RegisterHandlers(domain)
        
        cls.MOCKS().HANDLER().RegisterLambdaHandlers([
            'OnOrdered@Selfie',
            'OnDeliver@Selfie',
            'OnOrdered@Ephemeral',
            'OnOrdered@Transcribe',
        ])
        
        cls.MOCKS().HANDLER().MockLambdaHandlers(
            domain, {
                'OnOrdered@Selfie': cls.OnSelfieOrdered,
                'OnDeliver@Selfie': cls.OnSelfieDeliver,
                'OnOrdered@Ephemeral': cls.OnEphemeralOrdered,
                'OnOrdered@Transcribe': cls.OnTranscribeOrdered,
            })
