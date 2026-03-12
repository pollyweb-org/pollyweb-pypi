from pollyweb import UTILS
from PW_AWS.AWS_TEST import AWS_TEST
from PUBLISHER import PUBLISHER
from PUBLISHER_SUBSCRIBER import PUBLISHER_SUBSCRIBER
from PUBLISHER_UPDATE import PUBLISHER_UPDATE

from pollyweb import LOG


class PUBLISHER_TESTS(PUBLISHER, AWS_TEST):
    ''' 📤 Publisher: https://quip.com/sBavA8QtRpXu/-Publisher '''
    

    @classmethod
    def TestSubscribe(cls):

        sender = 'subscriber.com'
        receiver = 'publisher.com'
        filter = {'A':1}

        cls.ResetAWS(receiver)

        cls.HandleSubscribe(
            event= cls.NewMsg(
                sender= sender,
                receiver= receiver,
                subject= 'Subscribe@Publisher',
                body= {}))

        # 2nd time, safe.
        event = cls.NewMsg(
            sender= sender,
            receiver= receiver,
            subject= 'Subscribe@Publisher',
            body= {
                'Filter': filter
            })

        cls.HandleSubscribe(
            event= event) 

        cls.AssertEqual(
            given= [
                item.RemoveAtt('ItemVersion').Obj()
                for item in PUBLISHER_SUBSCRIBER._table().GetAll()
            ],
            expect= [{
                "ID": sender,
                "Filter": filter
            }])


    @classmethod
    def TestUnsubscribe(cls):
        
        receiver = 'publisher.com'

        cls.ResetAWS(receiver)
        table = PUBLISHER_SUBSCRIBER._table()

        cls.AssertEqual( len(table.GetAll()), 0 )

        cls.HandleSubscribe(
            event= cls.NewMsg(
                receiver= receiver,
                subject= 'Subscribe@Publisher',
                body= {}))
        
        cls.AssertEqual( len(table.GetAll()), 1 )
        
        cls.HandleUnsubscribe(
            event= cls.NewMsg(
                receiver= receiver,
                subject= 'Unsubscribe@Publisher',
                body= {}))

        cls.AssertEqual( len(table.GetAll()), 0 )


    @classmethod
    def TestPublish(cls):

        # Prepare publisher.
        cls.ResetAWS()

        cls.MOCKS().PUBLISHER().MockPublisher(publisher= 'any-publisher.com')

        # Confirm that there are no previous updates.
        cls.AssertEqual( len(PUBLISHER_UPDATE._table().GetAll()), 0 )
        
        # Happy path.
        event= cls.NewMsg(subject= 'Publish@Publisher')
        
        cls.HandlePublish(event)

        PUBLISHER_UPDATE._table().MatchCount(1)
        
        cls.AssertEqual(
            given= [
                item.RemoveAtt('ItemVersion').RemoveAtt('ID').Obj()
                for item in PUBLISHER_UPDATE._table().GetAll()
            ],
            expect= [{
                "Domain": event.RequireFrom(),
                "SentAt": event.GetTimestamp(),
                "Correlation": event.RequireCorrelation()
            }])
        
        # Dedup.
        cls.HandlePublish(event)
        PUBLISHER_UPDATE._table().MatchCount(1)

        # Ignore old events.
        event= cls.NewMsg(subject= 'Publish@Publisher')
        event.GetTimestamp(set= UTILS.ToTimestamp(UTILS.Yesterday()))
        cls.HandlePublish(event)
        PUBLISHER_UPDATE._table().MatchCount(1)


    @classmethod
    def TestReplay(cls):

        publisher = 'any-publisher.com'
        subscriber = 'any-subscriber.com'

        cls.ResetAWS()
        
        cls.MOCKS().PUBLISHER().MockPublisher(
            publisher= publisher, 
            subscribers= [subscriber])
        
        updates = cls.MOCKS().PUBLISHER().MockUpdates(
            publisher= publisher)

        # Send the message.
        event= cls.NewMsg(            
            sender= subscriber,
            subject= 'Replay@Publisher',
            body= { 
                'Since': "2000-01-01T00:00:00.000Z"
            })
        cls.HandleReplay(event)

        # Validate the subject for the subscriber.
        cls.AssertEqual(cls.Echo['Header']['To'], subscriber)
        cls.AssertEqual(cls.Echo['Header']['Subject'], 'Consume@Subscriber')
        
        # Varify if Consume@Subscriber message contains the given update.
        cls.AssertEqual(len(cls.Echo['Body']['Updates']), 10)
        update2 = cls.Echo['Body']['Updates'][0]
        
        cls.AssertNotEqual(
            cls.Echo['Body']['Token'], 
            None)

        cls.AssertEqual(
            update2['SentAt'], 
            updates[0]['SentAt'])
        
        cls.AssertEqual(
            update2['UpdateID'], 
            updates[0]['UpdateID'])
             

    @classmethod
    def TestNext(cls):

        publisher = 'publisher.com'
        subscriber = 'subscriber.com'

        cls.ResetAWS()
        
        cls.MOCKS().PUBLISHER().MockPublisher(publisher= publisher)

        cls.MOCKS().PUBLISHER().MockPublisher(
            publisher= publisher, 
            subscribers= [subscriber])
        
        cls.MOCKS().PUBLISHER().MockUpdates(
            publisher= publisher)
        
        token = cls.MOCKS().PUBLISHER().MockToken(
            publisher= publisher)

        # Send the message.
        event= cls.NewMsg(            
            sender= subscriber,
            subject= 'Next@Publisher',
            body= { 
                'Token': token
            })
        cls.HandleNext(event)

        # Validate the subject for the subscriber.
        cls.AssertEqual(cls.Echo['Header']['To'], subscriber)
        cls.AssertEqual(cls.Echo['Header']['Subject'], 'Consume@Subscriber')

        cls.AssertEqual(len(cls.Echo['Body']['Updates']), 2)
        update2 = cls.Echo['Body']['Updates'][1]
        cls.AssertTrue('Token' not in cls.Echo['Body'])
        cls.AssertEqual(update2['UpdateID'],19)


    @classmethod
    def TestAllPublisher(cls):
        LOG.Print('PUBLISHER_TESTS.TestAllPublisher() ==============================')

        cls.TestSubscribe()
        cls.TestUnsubscribe()
        cls.TestPublish()
        cls.TestReplay()
        cls.TestNext()


    @classmethod
    def MockManifester(cls):
        pass