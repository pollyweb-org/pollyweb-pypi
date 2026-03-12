from CONSUMER import CONSUMER
from PW_AWS.AWS_TEST import AWS_TEST
from SESSION import SESSION
from pollyweb import LOG
import json


class CONSUMER_TESTS(CONSUMER, AWS_TEST):
    

    @classmethod
    def TestQuery(cls): 
        LOG.Print('CONSUMER_TESTS.TestQuery() ==============================')

        broker = 'any-broker.org'
        consumer = 'any-consumer.org'

        cls.ResetAWS()
        cls.MOCKS().BROKER().MockBroker()

        # ---------------
        # EXECUTE CONSUMER
        # ---------------

        cls.SetDomain(consumer)
        cls.AssertEqual(len(cls.AWS().DYNAMO('SESSIONS').GetAll()), 2)

        cls.Query(
            session= SESSION.New(
                host= consumer,
                locator= '<locator>',
                broker= broker,
                sessionID= '<session-uuid@consumer>'
            ),
            message= '<my-message>',
            code= 'any-authority.org/<code>'
        )

        # ---------------
        # VERIFY
        # ---------------

        # Session on consumer.
        cls.SetDomain(consumer)

        sessions = cls.AWS().DYNAMO('SESSIONS')
        cls.AssertEqual(len(sessions.GetAll()), 2)

        cls.AssertEqual(
            given= sessions.GetAll()[0]['Queries'], 
            expect=['any-authority.org/<code>'])


    @classmethod
    def TestConsume(cls):
        LOG.Print('\nCONSUMER_TESTS.TestConsume() ==============================')

        cls.ResetAWS()
        
        vault = 'any-vault.org'
        broker = 'any-broker.org'
        consumer = 'any-consumer.org'
        graph = 'any-graph.com'

        # ---------------
        # SET UP CONSUMER
        # ---------------

        # Add the Query to the session.
        cls.TestQuery()

        # Set up the graph for the consumer.
        cls.MOCKS().GRAPH().MockGraph(graph)
        cls.MOCKS().SSM().MockSettings(
            domain= consumer,
            config= {
                'Graph': graph
            })

        # ---------------
        # SET UP VAULT
        # ---------------

        cls.MOCKS().VAULT().MockVault(vault)
        cls.MOCKS().BROKER().MockBroker(broker)

        # ---------------
        # EXECUTE CONSUMER
        # ---------------

        cls.SetDomain(consumer)

        vaultMsg = {
            "Header": {
                "From": vault,
                "To": consumer,
                "Subject": "Consume@Consumer"
            },
            "Body": {
                "Session": {
                    "Broker": "any-broker.org",
                    "SessionID": "<session-uuid>"
                },
                "Shared": {
                    "Code": "any-authority.org/<code>",
                    "Version": "1.0.0",
                    "UserData": "..."
                },
                "More": "<uuid>"
            }
        }

        cls.HandleConsume(vaultMsg)
        

    @classmethod
    def TestVerify(cls):
        LOG.Print('CONSUMER_TESTS.TestVerify() ==============================')

        broker = 'any-broker.org'
        consumer = 'any-consumer.org'

        cls.ResetAWS()
        cls.MOCKS().BROKER().MockBroker()

        cls.SetDomain(consumer)
        cls.HandleVerify({
            "Header": {
                "From": broker,
                "To": consumer,
                "Subject": "Verify@Consumer"
            },
            "Body": {
                "SessionID": "<session-uuid@consumer>",
                "Tokens": [{
                    "TokenID": "7bcf138b-db79-4a42-9d36-2655f8ff1f7c",
                    "Code": "any-authority.org/<code>",
                    "Version": "1.0.0",
                    "Issuer": "example.com",
                    "QR": "...",
                    "Issued": "2018-12-10T13:45:00.000Z",
                    "Starts": "2018-12-10T13:45:00.000Z",
                    "Expires": "2018-12-10T13:45:00.000Z"
                }]
            }
        })

        cls.AssertEqual(
            given= cls.AWS().DYNAMO('SESSIONS').Require('any-broker.org/<session-uuid@consumer>')['Tokens'][0], 
            expect= {
                'Code': 'airlines.any-igo.org/SSR/WCH', 
                'Version': '1.0.0', 
                'Issuer': 'example.com', 
                'ID': '7bcf138b-db79-4a42-9d36-2655f8ff1f7c', 
                'QR': '...'
            })
        

    @classmethod
    def TestAllConsumer(cls):
        LOG.Print('CONSUMER_TESTS.TestAllConsumer() ==============================')

        cls.TestQuery()
        cls.TestConsume()
        cls.TestVerify()