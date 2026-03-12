# 📚 SYNCAPI

from PW_AWS.AWS import AWS
from NLWEB import NLWEB
from pollyweb import LOG
from MSG import MSG
from ACTOR import ACTOR
from pollyweb import STRUCT
from pollyweb import UTILS


def test():
    return 'this is SYNCAPI test.'


class SYNCAPI(ACTOR):
    

    @classmethod
    def SENDER(cls):
        from SYNCAPI_SENDER import SYNCAPI_SENDER as proxy
        return proxy()
    

    @classmethod
    def RECEIVER(cls):
        from SYNCAPI_RECEIVER import SYNCAPI_RECEIVER as proxy
        return proxy()
    

    @classmethod
    def DKIM(cls):
        from SYNCAPI_DKIM import SYNCAPI_DKIM as proxy
        return proxy()
    
    
    @classmethod
    def Invoke(cls, msg:MSG=None, to:str=None, subject:str=None, body=None) -> STRUCT: 
        '''👉️ Sends a synchronous request to another domain.
        * This is a blocking call - i.e. waits for the remote answer.
        * Returns the remote answer as STRUCT.
        
        Params:
        * to: destination domain - e.g. any-domain.com
        * subject: the name of the method as <action>@<role> - e.g. Order@Supplier
        * body: the content dictionary to send (optional)
        '''

        LOG.Print(f' SYNCAPI.Invoke()', 
            f'{to=}', f'{subject=}')

        UTILS.AssertIsType(msg, MSG)
        UTILS.AssertIsType(to, str)
        UTILS.AssertIsType(subject, str)
        
        if msg == None:
            UTILS.RequireArgs([to, subject, body])
            msg = MSG.Wrap(to=to, subject=subject, body=body)

        msg.Stamp()
        envelope = msg.Envelope()

        sent = AWS.LAMBDA('SENDER').Invoke(envelope)
        return sent
