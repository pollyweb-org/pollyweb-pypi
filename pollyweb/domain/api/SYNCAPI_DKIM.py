# 📚 DKIM (part of SYNCAPI)

from pollyweb import STRUCT
from PW_AWS.AWS import AWS
from pollyweb import LOG
from pollyweb import UTILS



class DKIM_VALIDATOR(STRUCT):

    def Hash(self) -> str:
        return self.RequireStr('hash')
        
    def IsVerified(self) -> bool:
        return self.RequireBool('isVerified')
        

class SYNCAPI_DKIM(dict):


    def __to_json__(self):
        return {
            'forReal': self.forReal,
        }


    # REQUEST { text, publicKey, signature }
    # RESPONSE { hash, isVerified }
    def ValidateSignature(self, 
        text:str, 
        hash:str, 
        publicKey:str, 
        signature:str
    ) -> DKIM_VALIDATOR:
        ##LOG.Print(f'{UTILS.Timer().Elapsed()} Invoking validator...')

        UTILS.AssertIsType(text, str)
        UTILS.AssertIsType(hash, str)
        UTILS.AssertIsType(publicKey, str)
        UTILS.AssertIsType(signature, str)

        ret = AWS.LAMBDA('VALIDATOR').Invoke({
            'text': text,
            'hash': hash,
            'publicKey': publicKey,
            'signature': signature
        })
        
        return DKIM_VALIDATOR(ret)
    

    def HandleDkimCfn(self): 
        AWS.LAMBDA('ROTATOR').Invoke()


    def HandleDkimSetter(self, event):
        # 👉 https://repost.aws/knowledge-center/route53-resolve-dkim-text-record-error

        LOG.Print(f'@: {event=}')
        import os

        key:str = event['public_key']
        key = key.replace('-----BEGIN PUBLIC KEY-----', '')
        key = key.replace('-----END PUBLIC KEY-----', '')
        key = key.replace('\n', '')

        dkim = key[:200] + '""' + key[200:]
        hostedZoneId= os.environ['hostedZoneId']

        AWS.ROUTE53(hostedZoneId).AddTxtRecord(
            name = os.environ['dkimRecordName'], 
            value = f'"v=DKIM1;k=rsa;p={dkim};"')    
        

    def HandleGenerateKeyPair(self) -> dict:
        keys = AWS.LAMBDA('Generator').Invoke()
        ##LOG.Print(f'API.DKIM.HandleKeyPairRotator(): {keys=}')
        return keys

        
    def HandleRotator(self, event) -> None:
        LOG.Print(f'@: {event=}')

        # Get the keys.
        LOG.Print(f'@: Get the keys')
        keys = self.HandleGenerateKeyPair()

        # Set the Route53 DKIM with the public key.
        LOG.Print(f'@: Set Route53 DKIM with public key')
        AWS.LAMBDA('DkimSetter').Invoke({
            'public_key': keys['PublicKey']
        })

        # Store the key pair in Secrets Manager.
        LOG.Print(f'@: Store the key pair in Secrets Manager')
        AWS.LAMBDA('SecretSetter').Invoke(keys)


    def HandleSecretSetter(self, event):
        '''
        {
            "PublicKey": "my-public-key",
            "PrivateKey": "my-private-key"
        }
        '''
        ##LOG.Print(f'API.HandleSecretSetter: {event=}')

        AWS.SECRETS().Get('/NLWEB/PublicKey').SetValue(event['PublicKey'])
        AWS.SECRETS().Get('/NLWEB/PrivateKey').SetValue(event['PrivateKey'])


    def HandleSetAlias(self):
        import os
        r53 = AWS.ROUTE53(os.environ['hostedZoneId'])

        r53.AddApiGW(
            customDomain = os.environ['customDomain'], 
            apiHostedZoneId = os.environ['apiHostedZoneId'],
            apiAlias = os.environ['apiAlias'])
    

    def HandleAlerter(self):
        # TODO: copy from Manifester.Alerter.
        pass