from AWS_TEST import AWS_TEST
from PW_UTILS.STRUCT import STRUCT


class EVENTBRIDGE_MOCK_MESSAGE(STRUCT):

    QUEUE = []

    @classmethod
    def HasQueue(cls):
        '''Checks if there are messages to be processed.'''
        return len(cls.QUEUE) > 0
    

    @classmethod
    def Continue(cls):
        msg = cls._Dequeue()
        domain = msg.RequireDomain()
        AWS_TEST.SetDomain(domain)
        msg._Run()
        

    @classmethod
    def _Dequeue(cls):
        '''Returns the next message in the queue.'''
        return EVENTBRIDGE_MOCK_MESSAGE(cls.QUEUE.pop(0))
    

    def _Run(self):
        '''Execute the messages in the queue.'''
        action = self
        payload = action['Payload']
        detailType = action['DetailType']
        from EVENTBRIDGE_MOCK import EVENTBRIDGE_MOCK
        handler = EVENTBRIDGE_MOCK.Map[detailType]
        handler(payload)


    @classmethod
    def Append(cls, detailType, payload, domain):
        item = {
            'DetailType': detailType,
            'Payload': payload,
            'Domain': domain
        }
        item = EVENTBRIDGE_MOCK_MESSAGE(item)
        cls.QUEUE.append(item)
    

    def RequireDomain(self):
        return self.RequireStr('Domain')
    
    