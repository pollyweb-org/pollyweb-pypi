from MSG import MSG
from MESSENGER import MESSENGER
from MESSENGER_MOCKS import MESSENGER_MOCKS
from pollyweb import LOG


class MESSENGER_TESTS(MESSENGER_MOCKS, MESSENGER):


    @classmethod
    def TestPush(cls):
        LOG.Print('MESSENGER.TESTS.TestPush() ==============================')

        sender = 'sender.com'
        receiver = 'receiver.com'

        cls.ResetAWS()

        cls.MOCKS().WEB().MockDomain(receiver)
        cls._mockMessengerSender(sender)
        
        cls.SetDomain(sender)
        
        cls.Push(
            source= 'TestPush',
            to= receiver,
            subject= 'Sender@Messenger',
            body= {'A':1})

        cls.AssertEqual(
            given= cls.Echo['Body'],
            expect= {'A':1})
                

    @classmethod
    def _testHandlePublisher(cls, event):
        cls._testHandlePublisherReturn = event['detail']['Body']


    @classmethod
    def TestHandlePublisher(cls):
        LOG.Print('MESSENGER.TESTS.TestHandlePublisher() ==============================')

        receiver = 'receiver.com'
        method = 'Publisher@Messenger'

        # Initialize AWS.
        cls.ResetAWS()

        # The Publisher() will send to the BUS.
        # The bus will then trigger the final target handler.
        cls.MockHandler(
            domain= receiver,
            subject= method)

        # Mock the message to be received.
        m = MSG({})
        m.RequireFrom('sender.com')
        m.RequireTo(receiver)
        m.RequireSubject(method)
        m.Body({'A':1})
        m.Stamp()
        m.Sign(signature='<signature>', hash='<hash>')
        
        # Receive the event.
        cls.MOCKS().SYNCAPI().MockReceive(
            domain= receiver,
            event= m.Obj())
        
        # Validate the results.
        #cls.AssertEqual(TESTS.Echo, {})
        cls.AssertEqual(cls.Echo['detail']['Body'], m.Body())
    

    # =====================================
    # ALL TESTS
    # =====================================


    @classmethod
    def TestAllMessenger(cls):
        LOG.Print('MESSENGER_TESTS.TestAllMessenger() ==============================')

        cls.TestPush()
        cls.TestHandlePublisher()