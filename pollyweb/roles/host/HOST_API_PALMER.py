# 🤗 HOST

from pollyweb import LOG

from HOST_API_BASE import HOST_API_BASE


class HOST_API_PALMER(HOST_API_BASE):
    ''' 🤗 https://quip.com/s9oCAO3UR38A/-Host \n
    Events:
     * HandleFound@Host (required)
    '''

    
    @classmethod
    def HandleFound(cls, event):
        ''' 🖐️👉 https://quip.com/s9oCAO3UR38A#temp:C:TDD558f6d6e0c8346e4bc9302b17 
        "Body": {
            "Broker": "any-broker.org",
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",    
            "DeviceID": "MY-DEVICE",
            "Scanner": "airport.any-nation.org"
        }
        '''
        LOG.Print('🤗 HOST.HandleFound()', event)

        msg, session = cls.VerifySession(event, fromPalmist=True)
        msg.MatchSubject('Found@Host')

        msg.RequireStr('DeviceID')
        msg.RequireStr('Scanner')
        
        # Acts on the finding - e.g., open a gate if the user has a token.
        cls.TriggerLambdas('OnFound@Host', event)

