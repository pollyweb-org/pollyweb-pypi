# 📚 SENDER (part of SYNCAPI)
# 👉️ https://quip.com/NiUhAQKbj7zi


from NLWEB import NLWEB
from PW_AWS.AWS import AWS
from pollyweb import LOG
from MSG import MSG
from pollyweb import UTILS
import os


class SYNCAPI_SENDER():


    
    def SignMsg(self, 
        privateKey: str, 
        publicKey:str, 
        msg:MSG
    ) -> None:
        '''👉️ Signs the message with the private key.'''

        msg.Stamp()
        text = UTILS.Canonicalize(msg)

        ''' 👉️ https://hands-on.cloud/boto3-kms-tutorial/ '''
        # REQUEST { privateKey, publicKey, text }
        # RESPONSE { hash, signature, isVerified }
        signed = AWS.LAMBDA('SIGNER').Invoke({
            'privateKey': privateKey,
            'publicKey': publicKey,
            'text': text
        })

        if signed.RequireBool('isVerified') != True:
            LOG.RaiseException('The sending signature is not valid!')
        
        msg.Sign(
            hash= signed.RequireStr('hash'),
            signature= signed.RequireStr('signature'))
    
        

    def PublicKey(self): 
        return AWS.SECRETS().Get('/NLWEB/PublicKey').GetValue()
    

    def PrivateKey(self):
        return AWS.SECRETS().Get('/NLWEB/PrivateKey').GetValue()



    def Handle(self, event):
        ''' 👉️ https://quip.com/NiUhAQKbj7zi 
        { 
            "Header": {
                "To": "7b61af20-7518-4d5a-b7c0-eee17e54bf7a.dev.pollyweb.org",
                "Subject": "AnyMethod"
            }
        }
        '''    
        LOG.Print(f'🚀 SYNCAPI.Sender.Handle()')

        msg = MSG(event)
        
        msg.RequireFrom(default= NLWEB.CONFIG().RequireDomain())
        
        UTILS.AssertEqual(
            given= msg.RequireFrom(), 
            expect= NLWEB.CONFIG().RequireDomain(), 
            msg= 'A domain should only send messages from their own domain.')

        msg.Stamp()
        msg.VerifyHeader()
        
        self.SignMsg(
            privateKey= self.PrivateKey(), 
            publicKey= self.PublicKey(), 
            msg= msg)

        sent = msg.Send()
        return sent