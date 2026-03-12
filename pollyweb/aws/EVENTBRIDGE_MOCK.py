
from EVENTBRIDGE_MOCK_MESSAGE import EVENTBRIDGE_MOCK_MESSAGE
from LOG import LOG

class EVENTBRIDGE_MOCK:

    ASYNC = False

    @classmethod
    def QUEUE(cls): 
        return EVENTBRIDGE_MOCK_MESSAGE()

    Map:dict[str,object] = {}

    @classmethod 
    def ResetMock(cls):
        EVENTBRIDGE_MOCK.Map = {}


    @classmethod
    def SetMockDomain(cls, domain:str):
        EVENTBRIDGE_MOCK._activeDomain = domain


    @classmethod 
    def MockHandlers(cls, map:dict[str,object]):
        EVENTBRIDGE_MOCK.Map.update(map)


    @classmethod 
    def MockHandler(cls, subject:str, handler:object):
        new = {}
        new[subject] = handler
        EVENTBRIDGE_MOCK.Map.update(new)

        
    
    @classmethod
    def Publish(cls, eventBusName:str, source:str, detailType:str, detail:any):
        LOG.Print(f'🚌 BUS.MOCK.Publish()', 
            f'{source=}', f'{detailType=}', 'detail=', detail)

        if detailType not in EVENTBRIDGE_MOCK.Map:
            ##LOG.Print(f'AWS.BUS.MOCK.Publish(): {MOCK_BUS.Map=}')
            LOG.RaiseValidationException(f'Unknown subject: {detailType}!')

        payload = {
            "version": "0",
            "id": "fe8d3c65-xmpl-c5c3-2c87-81584709a377",
            "detail-type": detailType,
            "source": source,
            "account": "123456789012",
            "time": "2020-04-28T07:20:20Z",
            "region": "us-east-2",
            "resources": [],
            "detail": detail
        }

        if cls.ASYNC == True: 
            # Add to the queue.
            cls.QUEUE().Append(
                detailType = detailType,
                payload = payload,
                domain = EVENTBRIDGE_MOCK._activeDomain)
            
        else:
            # Execute now.
            handler = EVENTBRIDGE_MOCK.Map[detailType]
            handler(payload)
