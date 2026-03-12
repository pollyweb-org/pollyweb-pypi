# 📚 MESSENGER

from PW_AWS.AWS import AWS
from NLWEB import NLWEB
from MESSENGER_CALLBACK import MESSENGER_CALLBACK
from MSG import MSG
from pollyweb import UTILS
from pollyweb import LOG


# ✅ DONE
class MESSENGER():
    ''' 🐌 Messenger behaviour of a domain.
    * https://quip.com/Fxj4AdnE6Eu5/-Messenger

    Sending from source domain:
    1. `ACTOR1` -> MESSENGER.Push('AsyncMethod@ACTOR2', msg)
    2. `MESSENGER` -> BUS.Publish('Sender@Messenger', msg)
    3. `BUS` -> Sender@MESSENGER(msg)
    4. `Sender@MESSENGER` -> SYNCAPI.Send(msg) 
    
    Receiving at destination domain:
    * `Receiver@SYNCAPI` -> Invoke(Publisher@MESSENGER, msg)
    * `Publisher@MESSENGER` -> BUS.Publish('AsyncMethod@ACTOR2', msg)
    * `BUS` -> ACTOR2.HandleAsyncMethod(msg)
    '''
    

    @classmethod
    def _publish(cls, msg:MSG, source:str, target:str):
        ''' 👉 Publishes a message to the BUS. '''   

        LOG.Print(
            f'🐌 MESSENGER._publish()', 
            msg, f'{source=}', f'{target=}')     
        
        # Validate if there's a destination domain.
        msg.RequireFrom(default= NLWEBBBB.CONFIG().RequireDomain())            
        msg.VerifyHeader()

        # Send to the bus.
        AWS.BUS().Publish(
            eventBusName= 'Messenger-Bus', 
            source= source,
            detailType= target, 
            detail= msg.Envelope())


    @classmethod
    def Push(cls, 
        source:str, to:str, subject:str, body:dict=None,
        callback:str=None, context: dict=None):
        ''' 👉 Publishes a message to the BUS, to be sent to another 
        domain via Publisher@Messenger. 

        Params: 
        * source: Name of the source component, for the message bus.
        * to: Destination domain name - e.g., any-broker.org
        * subject: Name of the destination handler - e.g., Offer@Broker
        * body: Optional content for the body - e.g., {}
        * callback: Lambda handler responsible receive the response.
        * context: Additional info about the initial call.
        '''
        LOG.Print(
            f'🐌 MESSENGER.Push()', 
            f'{source=}', f'{to=}', f'{subject=}',
            f'body=', body)

        UTILS.RequireArgs([source, to, subject])

        # Wrap into a message envelope.
        msg = MSG.Wrap(
            to=to, 
            body=body, 
            subject=subject)
        
        # If there's a callback handler, then save the correlation.
        if callback != None:
            MESSENGER_CALLBACK.Insert(
                correlation= msg.RequireCorrelation(),
                domain= to,
                handler= callback,
                context= context)
        
        # Send to the bus.
        cls._publish(
            msg= msg, 
            source= source,
            target= 'Sender@Messenger')
        

    def InvokeCallback(cls, source:str, request:MSG, response:dict):
        ''' 👉 Returns a slow reponse from an async request.'''

        UTILS.RequireArgs([source, request, response])
        MSG.AssertClass(request)

        cls.Push(
            source= source,
            to= request.RequireFrom(),
            subject= 'Callback@Messenger',
            body= {
                'Correlation': request.RequireCorrelation(),
                'Response': response
            })


    @classmethod
    def HandlePublisher(cls, event):
        ''' 👉 Publishes a received msg to the BUS, to be handled by internal logic.'''
        UTILS.RequireArgs([event])

        msg = MSG(event)
        msg.VerifyHeader()

        # Send the msg to the bus, to be handled by a Lambda.
        cls._publish(
            msg= msg, 
            source= 'Publisher@Messenger',
            target= msg.RequireSubject())
        
        
    @classmethod
    def HandleCallback(cls, event):
        ''' 👉 Handled the response to a previously sent message.'''
        
        msg = MSG(event)

        # Get the callback stored.
        callback = MESSENGER_CALLBACK.RequireCallback(
            correlation= msg.RequireUUID('Correlation'))

        # Check if the domains match.
        UTILS.AssertEqual(
            given= msg.RequireFrom(), 
            expect= callback.RequireDomain(), 
            msg='The callback was not for this domain!')
        
        # Execute the lambda with the original correlation and context.
        alias = callback.RequireHandler()
        params = {
            'Correlation': msg.RequireCorrelation(),
            'Domain': callback.RequireDomain(),
            'Context': callback.RequireContext(),
            'Response': msg.RequireStruct('Response')
        }
        AWS.LAMBDA(alias).Invoke(params)


    @classmethod
    def HandleSender(cls, event):
        ''' 👉️ Collects msgs from the BUS, and sends them to the SyncAPI.
        * https://quip.com/NiUhAQKbj7zi'''
        
        ##LOG.Print(f'MESSENGER.HandleSender()')

        # Get the detail from the BUS event.
        detail = event['detail']

        # Parse the message.
        msg = MSG(detail)

        # Stamp again, just in case.
        msg.Stamp()

        # Check if all is good before sending forward.
        msg.VerifyHeader()
        
        # Send to the SyncAPI.
        return NLWEB.BEHAVIORS().SYNCAPI().Invoke(msg= msg)


