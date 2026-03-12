from NLWEB import NLWEB
from PW_AWS.AWS_TEST import AWS_TEST
from MESSENGER import MESSENGER


class MESSENGER_MOCKS(MESSENGER, AWS_TEST):


    @classmethod
    def _mockMessengerSender(cls, domain:str):
        '''👉 Prepares the MESSENGER to send messages.'''

        cls.MOCKS().SYNCAPI().MockSyncApi(domain)

        cls.MOCKS().BUS().MockHandler(
            subject= 'Sender@Messenger', 
            handler= cls.HandleSender)
        

    @classmethod
    def _mockMessengerReceiver(cls, domain:str):
        '''👉 Prepares the MESSENGER to receive messages.'''
        
        # Set up the Sync API.
        cls.MOCKS().SYNCAPI().MockSyncApi(domain= domain)

        # Add a map to async callback.
        cls.MockHandler(
            domain= domain, 
            subject= 'Callback@Messenger',
            ignoreValidation= False,
            handler= cls.HandleCallback)
        

    @classmethod
    def MockMessenger(cls, domain:str):

        # Confirm it wasn't mocked already.
        if cls.IsDomainMocked(domain=domain, component=cls):
            return
        
        cls._mockMessengerReceiver(domain= domain)
        cls._mockMessengerSender(domain= domain)


    @classmethod
    def MockHandler(cls, 
                    domain:str, 
                    subject:str, 
                    ignoreValidation:bool = False,
                    handler:object=AWS_TEST._echo):

        cls.MockMessenger(domain)

        # The SyncAPI will call the Messenger.Publisher()
        cls.MOCKS().SYNCAPI().MockHandler(
            domain= domain, 
            subject= subject, 
            ignoreValidation= ignoreValidation,
            handler= cls.HandlePublisher)

        # The Publisher() will send to the BUS.
        # The bus will then trigger the final target handler.
        cls.AWS().BUS().MockHandler(
            subject= subject, 
            handler= handler)
        

    @classmethod
    def MockHandlers(cls, domain:str, pairs:dict[str,object], ignoreValidation:bool=False):
        # Add all pairs to the MAP table on SYNCAPI.

        for subject in pairs.keys():
            cls.MockHandler(
                domain= domain,
                subject= subject,
                ignoreValidation= ignoreValidation,
                handler= pairs[subject])