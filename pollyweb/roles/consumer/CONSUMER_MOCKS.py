from CONSUMER import CONSUMER
from PW_AWS.AWS_TEST import AWS_TEST
from HOST_MOCKS import HOST_MOCKS
from pollyweb import LOG


class CONSUMER_MOCKS(CONSUMER, HOST_MOCKS, AWS_TEST):


    @classmethod
    def MockConsumerSetup(cls, consumer:str, clean:bool):
        LOG.Print(' CONSUMER.MOCKS.MockConsumerSetup()', f'{consumer=}')

        # HOST setup.
        cls.MOCKS(consumer).HOST().MockHostSetup(consumer, clean=clean)

        # Additional MSG handlers.
        cls.MOCKS(consumer).MESSENGER().MockHandlers(
            domain= consumer,
            ignoreValidation= False, 
            pairs= {
                'Consume@Consumer': cls.HandleConsume,
                'Verify@Consumer': cls.HandleVerify,
                'WontShare@Consumer': cls.HandleWontShare
            })
        
        # Additional TRIGGER handlers.
        cls.MOCKS(consumer).HANDLER().RegisterLambdaHandlers(
            events= [
                'OnConsume@Consumer',
                'OnVerify@Consumer'
            ])
        

    @classmethod
    def MockConsumerSessions(cls, consumer:str, broker:str, clean:bool):
    
        cls.MockHostSession(host=consumer, broker=broker, clean=clean)

        # Additional SESSIONS.
        if not clean:
            cls.AddSession(
                host= consumer,
                broker= broker,
                sessionID= '<session-uuid@consumer>'
            )


    @classmethod
    def MockConsumerConfigs(cls, consumer:str, graph:str, clean:bool):

        # Set up the GRAPH.
        if clean != True:
            cls.MOCKS().GRAPH().MockGraph(
                graph= graph, 
                manifest= consumer)
        
        # Point to the GRAPH.
        cls.MockHostConfigs(
            host= consumer,
            graph= graph, 
            clean= clean)
        
        # Add VAULTS to bindable codes.
        if not clean:
            cls.MOCKS().DYNAMO().MockTable(
                domain= consumer,
                table= 'CODES',
                items= [{
                    'ID': 'any-authority.org/<code>',
                    'Vaults': ['any-vault.org', 'any-consumer.org']
                }]
            )

        

    @classmethod
    def MockConsumer(cls, 
        consumer:str= 'any-consumer.org',
        broker:str= 'any-broker.org',
        graph:str= 'any-graph.com',
        clean:bool=False):
        
        cls.SetDomain(consumer)
        
        if cls.IsDomainMocked(domain=consumer, component=cls):
            return
        
        cls.MockConsumerSetup(
            consumer= consumer,
            clean= clean)
        
        cls.MockConsumerConfigs(
            consumer= consumer,
            graph= graph,
            clean= clean)

        cls.MockConsumerSessions(
            consumer= consumer,
            broker= broker, 
            clean= clean)

        cls.SetDomain(consumer)
