from PW_AWS.AWS_TEST import AWS_TEST
from PUBLISHER import PUBLISHER
from PW_AWS.DYNAMO_MOCK import DYNAMO_MOCK
from pollyweb import UTILS


class PUBLISHER_MOCKS(PUBLISHER, AWS_TEST):
    
    
    @classmethod
    def MockPublisherSetup(cls, publisher:str):

        if cls.IsDomainMocked(publisher, cls) == True:
            return
        
        cls.MOCKS().MESSENGER().MockMessenger(domain= publisher)
        
        cls.MOCKS(publisher).HANDLER().RegisterLambdaHandlers(
            events= [
                'OnEnrich@Publisher',
                'OnFilter@Publisher'
            ])

        # Register internal handlers.
        cls.MOCKS().MESSENGER().MockHandlers(
            domain= publisher,
            ignoreValidation= False,
            pairs= {
                'Next@Publisher': cls.HandleNext,
                'Publish@Publisher': cls.HandlePublish,
                'Replay@Publisher': cls.HandleReplay,
                'Subscribe@Publisher': cls.HandleSubscribe,
                'Unsubscribe@Publisher': cls.HandleUnsubscribe
            })

        # Register custom handlers.
        DYNAMO_MOCK.MockTable(
            domain= publisher,
            table= 'TRIGGERS', 
            items=[
                {
                    "ID": 'OnEnrich@Publisher',
                    "Lambdas": []
                },
                {
                    "ID": 'OnFilter@Publisher',
                    "Lambdas": []
                }
            ])
        
        cls.SetDomain(domain=publisher)



    @classmethod
    def MockSubscriber(cls, 
                      publisher='any-publisher.com', 
                      subscriber='any-subscriber.com'):

        UTILS.AssertIsType(subscriber, str)

        cls.SetDomain(publisher)

        cls.AWS().DYNAMO('SUBSCRIBERS').Upsert({
            "ID": subscriber,
            "Filter": {}
        })
        
        cls.MOCKS().WEB().MockDomain(domain= subscriber)

        cls.SetDomain(publisher)


    @classmethod
    def MockUpdates(cls,
                    publisher:str = 'any-publisher.com'
                    ) -> list:
        
        # Add old updates.
        updates = [
            {
                "ID": f"any-domain-{id}.com",
                "SentAt": "2018-12-10T13:45:00.000Z",
                "UpdateID": str(id),
                "Correlation": cls.UTILS().Correlation()
            }
            for id in range(20)
        ]
        
        DYNAMO_MOCK.MockTable(
            domain= publisher,
            table= 'DOMAINS', 
            items=updates)
        
        return updates


    @classmethod 
    def MockToken(cls,
                  publisher:str = 'any-publisher.com'
                  ) -> str:
        
        cls.SetDomain(publisher)

        id = '8e8cb55b-55a8-49a5-9f80-439138e340a2'
        cls.AWS().DYNAMO('TOKENS').Insert({
            'ID': id,
            "LastEvaluatedKey": "{\"ID\": \"any-domain-17.com\"}",
            "SentAt": "2000-01-01T00:00:00.000Z",
            "Domain": "subscriber.com"
        })

        return id
    

    @classmethod
    def MockPublisher(cls, 
        publisher:str = 'any-publisher.com',
        subscribers:list[str] = ['any-subscriber.com']
    ):

        cls.MockPublisherSetup(publisher= publisher)

        for subscriber in subscribers:
            cls.MockSubscriber(
                publisher= publisher, 
                subscriber= subscriber)

        cls.SetDomain(domain= publisher)