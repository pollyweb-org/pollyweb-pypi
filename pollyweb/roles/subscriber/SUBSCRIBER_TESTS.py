from SUBSCRIBER import SUBSCRIBER
from PW_AWS.AWS_TEST import AWS_TEST
from pollyweb import UTILS
from pollyweb import LOG


class SUBSCRIBER_TESTS(SUBSCRIBER, AWS_TEST):


    @classmethod
    def TestUpdated(cls):

        receiver = 'any-subscriber.com'

        cls.ResetAWS()
        cls.MOCKS().SUBSCRIBER().MockSubscriber(
            subscriber= receiver,
            onStreamHandler= None)

        # Mock the update to a domain.
        update = cls.NLWEB().INTERFACES().UPDATE().New(
            updateID= UTILS.UUID(),
            domain= 'any-domain.com',
            timestamp= UTILS.GetTimestamp(), 
            correlation= UTILS.Correlation())
                
        # Mock the message to be received.
        m = cls.NewMsg(
            receiver= 'any-subscriber.com',
            subject= 'Updated@Subscriber',
            body= update
        )

        # Receive the event.
        cls.MOCKS().SYNCAPI().MockReceive(
            domain= receiver,
            event= m.Obj())


    @classmethod
    def TestConsume(cls):

        receiver = 'any-subscriber.com'
        method = 'Consume@Subscriber'

        cls.ResetAWS()
        cls.MOCKS().SUBSCRIBER().MockSubscriber(
            subscriber= receiver,
            onStreamHandler= None)

        # Mock the update to a domain.
        update = cls.NLWEB().INTERFACES().UPDATE().New(
            updateID= UTILS.UUID(),
            domain= 'any-domain.com',
            timestamp= UTILS.GetTimestamp(),
            correlation= UTILS.Correlation()
        )

        updates = {
            'Updates': [
                update.Obj()
            ]
        }
                
        # Mock the message to be received.
        m = cls.NLWEB().INTERFACES().MSG({})
        m.RequireFrom('sender.com')
        m.RequireTo(receiver)
        m.RequireSubject(method)
        m.Body(updates)
        m.Stamp()
        m.Sign(signature='<signature>', hash='<hash>')

        # Receive the event.
        cls._testUpdatedResult = None
        cls.MOCKS().SYNCAPI().MockReceive(
            domain= receiver,
            event= m.Obj())

        '''
        cls.AssertEqual(
            given= cls.Echo['Body'],
            expect= update)
        '''
    

    @classmethod
    def TestAllSubscriber(cls):
        LOG.Print('SUBSCRIBER_TESTS.TestAllSubscriber() ==============================')

        cls.TestUpdated()
        cls.TestConsume()
        