from SUBSCRIBER import SUBSCRIBER
from PW_AWS.AWS_TEST import AWS_TEST


class SUBSCRIBER_MOCKS(SUBSCRIBER, AWS_TEST):


    @classmethod
    def MockSubscriberSetup(cls, domain):
        
        # MSG handlers.
        cls.MOCKS().SYNCAPI().MockHandlers(
            domain= domain,
            ignoreValidation= False,
            pairs= {
                'Consume@Subscriber': cls.HandleConsume,
                'Updated@Subscriber': cls.HandleUpdated
            })
        
        # TRIGGER handlers.
        cls.MOCKS().HANDLER().RegisterLambdaHandlers(
            events= ['OnUpdated@Subscriber'])


    @classmethod
    def MockSubscriber(cls, 
                       onStreamHandler:object,
                       subscriber:str='any-subscriber.com'):
        
        if cls.IsDomainMocked(subscriber, cls) == True:
            return
        
        cls.MockSubscriberSetup(domain=subscriber)

        cls.MOCKS(subscriber).DYNAMO('DEDUPS').OnStream(
            handler= onStreamHandler)
        
