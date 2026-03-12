# 📚 SUBSCRIBER

from NLWEB import NLWEB
from pollyweb import LOG
from UPDATE import UPDATE
from PW_UTILS.HANDLER import HANDLER
from MSG import MSG
from SUBSCRIBER_DEDUP import SUBSCRIBER_DEDUP
from pollyweb import UTILS
from pollyweb import STRUCT


# ✅ DONE
class SUBSCRIBER(HANDLER):
    ''' 📥 Subscriber: https://quip.com/9ab7AO56kkxY/-Subscriber '''
    

    @classmethod
    def InvokeUpdated(cls, source:str, to:str, update:[STRUCT,UPDATE]=None):
        ''' 👉 Receive notification about an update to a domain.
        * https://quip.com/9ab7AO56kkxY#temp:C:ISdeb655f34cef549fbbb9669e4a '''

        LOG.Print(f'📥 SUBSCRIBER.InvokeUpdated()', f'{source=}', f'{to=}')

        UTILS.RequireArgs([source, to])

        if update != None:
            if isinstance(update, STRUCT):
                update = UPDATE(update)
            if isinstance(update, UPDATE):
                update.Verify()
            UTILS.AssertIsType(update, UPDATE)

        return NLWEB.BEHAVIORS().MESSENGER().Push(
            source= source,
            subject= 'Updated@Subscriber',
            to= to,
            body= update)
    

    @classmethod
    def HandleUpdated(cls, event):
        ''' 📤🐌 https://quip.com/9ab7AO56kkxY#temp:C:ISdeb655f34cef549fbbb9669e4a 
        "Body": {
            "UpdateID": "8e8cb55b-55a8-49a5-9f80-439138e340a2",
            "Domain": "example.com",
            "SentAt": "2018-12-10T13:45:00.000Z"
        }
        '''
        LOG.Print(
            f'📥 SUBSCRIBER.HandleUpdated()', 
            f'domain={NLWEB.CONFIG().RequireDomain()}')

        msg = MSG(event)
        msg.MatchSubject('Updated@Subscriber')

        if SUBSCRIBER_DEDUP.Upsert(msg):
            cls.TriggerLambdas(
                event= 'OnUpdated@Subscriber',
                payload= msg)
                

    @classmethod
    def InvokeConsume(cls, request:MSG, source:str, token:str, updates:list[UPDATE]):
        ''' 📤🐌 https://quip.com/9ab7AO56kkxY#temp:C:ISd000c9e83bc4945b293024175e '''

        body = {}
        body['Updates'] = updates
        if token:
            body['Token'] = token
            
        return NLWEB.BEHAVIORS().MESSENGER().Push(
            subject= 'Consume@Subscriber',
            to= request.RequireFrom(),
            source= source,
            body= body)


    @classmethod
    def HandleConsume(cls, page):
        ''' 📤🐌 https://quip.com/9ab7AO56kkxY#temp:C:ISd000c9e83bc4945b293024175e \n
        "Body": {
            "Updates":[
                {
                    "UpdateID": "8e8cb55b-55a8-49a5-9f80-439138e340a2",
                    "Domain": "example.com",
                    "SentAt": "2018-12-10T13:45:00.000Z",
                    "Correlation": "<uuid>"
                }
            ],
            "Token": "cdaf19d8-3e51-4f1f-b5c7-2c7d9dda0c0d"
        }
        '''
        msg = MSG(page)
        msg.MatchSubject('Consume@Subscriber')

        # Execute individual updates.
        for update in msg.Body()['Updates']:
            UPDATE(update).Verify()

            single = MSG({})
            single.RequireHeader(msg.RequireHeader())
            single.Body(update)
            single.RequireSubject('Updated@Subscriber')
            
            cls.HandleUpdated(single)

        # Ask for the next group of updates.
        if not msg.IsMissingOrEmpty('Token'):
            NLWEB.BEHAVIORS().PUBLISHER().InvokeNext(
                token= msg.RequireAtt('Token'),
                request= msg,
                source='Subscriber-Consume')
            