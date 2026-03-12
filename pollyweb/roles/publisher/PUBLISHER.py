'''
📤 PUBLISHER
├─ handles Register(), Unregister(), and Subscribe()
│  └─ writes to Subscribers table 
├─ handles Updated()
│  ├─ writes to Updates table 
│  └─ sends to Messenger
└──handles Replay(), and Next()
    ├── reads from Updates table
    ├── writes to Tokens table
    └─ sends to Messenger
'''

from NLWEB import NLWEB
from pollyweb import LOG
from UPDATE import UPDATE
from PW_UTILS.HANDLER import HANDLER
from MSG import MSG
from pollyweb import UTILS
from PUBLISHER_CORRELATION import PUBLISHER_CORRELATION
from PUBLISHER_DOMAIN import PUBLISHER_DOMAIN
from PUBLISHER_SUBSCRIBER import PUBLISHER_SUBSCRIBER
from PUBLISHER_TOKEN import PUBLISHER_TOKEN
from PUBLISHER_UPDATE import PUBLISHER_UPDATE


# ✅ DONE
class PUBLISHER(HANDLER):
    ''' 📤 Publisher: https://quip.com/sBavA8QtRpXu/-Publisher '''
    

    def InvokeSubscribe(self, source:str, publisher:str, filter:object={}):
        NLWEB.BEHAVIORS().MESSENGER().Push(
            source= source,
            to= publisher,
            subject= 'Subscribe@Publisher',
            body= {
                "Filter": filter
            })


    @classmethod
    def HandleSubscribe(cls, event):
        ''' 🐌 https://quip.com/sBavA8QtRpXu/-Publisher#temp:C:IEKf5f88769121840418de6755e4 
        {
            "Header": {
                "From": "38ae4fa0-afc8-41b9-85ca-242fd3b735d2.dev.pollyweb.org"
            }
            "Body": {
                "Filter": {}
            }
        }
        '''
        msg = MSG(event)
        
        PUBLISHER_SUBSCRIBER().Upsert(msg)


    @classmethod
    def HandleUnsubscribe(cls, event):
        ''' 🐌 https://quip.com/sBavA8QtRpXu#temp:C:IEK2b8247c67fae4d4487321c2e1 
        {
            "Header": {
                "From": "38ae4fa0-afc8-41b9-85ca-242fd3b735d2.dev.pollyweb.org"
            }
        }
        '''
        msg = MSG(event)
        PUBLISHER_SUBSCRIBER.RequireSubscriber(msg).Delete()

    
    @classmethod
    def HandlePublish(cls, event):
        ''' 🐌 https://quip.com/sBavA8QtRpXu/-Publisher#temp:C:IEK5a453bcdb55e4d41bcc57bbc6 
        {
            "Header": {
                "From": "38ae4fa0-afc8-41b9-85ca-242fd3b735d2.dev.pollyweb.org"
            }
        }
        '''
        LOG.Print(
            f'📤 PUBLISHER.HandlePublish()', 
            f'domain= {NLWEB.CONFIG().RequireDomain()}', event)

        msg = MSG(event)

        # Check for duplicates.
        if not PUBLISHER_CORRELATION.GetCorrelation(msg).IsMissingOrEmpty():
            LOG.Print(
                f'📤 PUBLISHER.HandlePublish:',
                'Duplicate event, ignoring.')
            return 
        
        # Check for old events.
        domain = PUBLISHER_DOMAIN.GetDomain(msg)
        if not domain.IsMissingOrEmpty():
            if domain.GetTimestamp() >= msg.GetTimestamp():
                LOG.Print(
                    f'📤 PUBLISHER.HandlePublish:', 
                    'Old event, ignoring.')
                return 
        
        # save to Updates table.
        raw = PUBLISHER_UPDATE().New(msg)

        update = cls.TriggerLambdas(
            event='OnEnrich@Publisher', 
            payload=raw)
        
        LOG.Print(
            f'📤 PUBLISHER.HandlePublish:',
            'Inserting update...', update)
        PUBLISHER_UPDATE.Insert(update)

        update.RemoveAtt('ItemVersion', safe=True)
    
        # save to Domains table.
        PUBLISHER_DOMAIN().Upsert(raw)

        # save to Correlations table.
        PUBLISHER_CORRELATION().Insert(msg)

        # TODO: this should be a DynamoDB stream event, to be more resilient.
        #   If the second step fails, a new UpdateID is inserted, growing to infinite.
        #   By separating the second step, it can fail independently with adding DB items.

        # fan out to all subscribers.
        subscribers = PUBLISHER_SUBSCRIBER.AllSubscribers()
        LOG.Print(
            f'📤 PUBLISHER.HandlePublish:', 
            f'subscribers={[x.RequireID() for x in subscribers]}')

        for subscriber in subscribers: 
            LOG.Print(
                f'📤 PUBLISHER.HandlePublish:',
                f'subscriber={subscriber.RequireID()}')

            if not cls._ignore(update, subscriber):
                LOG.Print(
                    f'📤 PUBLISHER.HandlePublish:',
                    f'invoking update to={subscriber.Domain()}', 
                    f'at={subscriber.RequireID()}',
                    f'update=', update)

                NLWEB.BEHAVIORS().SUBSCRIBER().InvokeUpdated(
                    source= 'Publish@Publisher',
                    update= update, 
                    to= subscriber.Domain())
            

    @classmethod
    def _ignore(cls, update, subscriber:PUBLISHER_SUBSCRIBER):
         ''' 👉 Verify if the subscriber asked this to be filtered. '''
         payload = {
             'Update': update,
             'Subscriber': subscriber.Obj(),
             'Ignore': False
         }

         result = cls.TriggerLambdas(
             event='OnFilter@Publisher', 
             payload= payload)
         
         return result.RequireBool('Ignore')
             

    @classmethod
    def HandleReplay(cls, replay):
        ''' 📥🐌 https://quip.com/sBavA8QtRpXu/-Publisher#temp:C:IEK1a95aeba490844ce9168b7f4d '''

        '''
        {
            "Header": {
                "From": "38ae4fa0-afc8-41b9-85ca-242fd3b735d2.dev.pollyweb.org"
            },
            "Body": {
                "Since": "2023-06-10T13:45:00.000Z"
            }
        }
        '''
        msg = MSG(replay)
        since = msg.Body().RequireTimestamp('Since')
        
        # Verify if the requester is registered.
        subscriber = PUBLISHER_SUBSCRIBER.RequireSubscriber(msg)
        
        cls._replay(
            request=msg, 
            since= since, 
            subscriber= subscriber,
            timestampColumn= 'SentAt')


    @classmethod
    def _replay(cls, 
        request:MSG, 
        since:str, 
        subscriber:PUBLISHER_SUBSCRIBER, 
        lastEvaluatedKey=None,
        timestampColumn:str= 'Timestamp'
    ):
        ''' 🏃 Supports Replay() and Next().
        
        Arguments:
            request {MSG} -- The original message.
            since {str} -- The timestamp to start from.
            subscriber {PUBLISHER_SUBSCRIBER} -- The subscriber to send the updates to.
            lastEvaluatedKey {any} -- The last evaluated key to continue the replay.
            timestampColumn {str} -- The column to filter the timestamp.
        '''
        
        # TODO Don't send empty pages.
        #   Fill require to loop through the pages, or to set a filter().
        #   Actually, filters won't work because the filter is external on self._ignore().

        domains, lastEvaluatedKey = PUBLISHER_DOMAIN.GetPageFromTimestamp(
            timestamp= since, 
            exclusiveStartKey= lastEvaluatedKey,
            timestampColumn= timestampColumn)

        items:list[UPDATE] = []
        for domain in domains:
            update = domain.ToUpdate()
            if not cls._ignore(update, subscriber):
                items.append(update)
        
        token = None
        if lastEvaluatedKey != None:
            item = PUBLISHER_TOKEN.Insert(
                lastEvaluatedKey= lastEvaluatedKey,
                timestamp= since, 
                domain= request.RequireFrom()
            )
            token = item.RequireID()

        ##LOG.Print(f'PUBLISHER._replay(): invoking consume with items={items}')
        NLWEB.BEHAVIORS().SUBSCRIBER().InvokeConsume(
            request= request, 
            source= 'Publisher-Replay',
            updates= items,
            token= token)
    

    def InvokeNext(self, source:str, request:MSG, token:str):
        ''' 🏃 Invokes Next@Publisher'''
        NLWEB.BEHAVIORS().MESSENGER().Push(
            source= source,
            to= request.RequireFrom(),
            subject= 'Next@Publisher',
            body= {
                'Token': token
            }
        )


    @classmethod
    def HandleNext(cls, event):
        ''' 🐌 https://quip.com/sBavA8QtRpXu#temp:C:IEK9f614503f0d44441a02dcf37f 
        "Body": {
            "Token": "8e8cb55b-55a8-49a5-9f80-439138e340a2"
        }
        '''
        msg = MSG(event)

        # Check if the token belongs to this domain.
        token = PUBLISHER_TOKEN.RequireToken(msg)

        # Check if it's an active subscriber.
        subscriber = PUBLISHER_SUBSCRIBER.RequireSubscriber(msg)

        # Get the next updates
        lastEvaluatedKey = token.LastEvaluatedKey()
        timestamp = token.GetTimestamp()

        return cls._replay(
            request= event, 
            since= timestamp, 
            subscriber= subscriber,
            lastEvaluatedKey= lastEvaluatedKey, 
            timestampColumn= 'SentAt')
    