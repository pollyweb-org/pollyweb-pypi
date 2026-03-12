from pollyweb import STRUCT
from PW_AWS.AWS_TEST import AWS_TEST
from SYNCAPI import SYNCAPI
from MSG import MSG
from pollyweb import LOG

import json


class SYNCAPI_TESTS(SYNCAPI, AWS_TEST):


    # =====================================
    # SENDER
    # =====================================


    @classmethod
    def TestSignMsg(cls):
        
        cls.ResetAWS()

        cls.MOCKS().SYNCAPI().MockSyncApi()

        # Sign with the key pair.
        msg = MSG({})
        
        cls.SENDER().SignMsg(
            privateKey= "priv", 
            publicKey= "pub", 
            msg= msg)
        
        msg.VerifySignature(
            publicKey= "pub")
        

    @classmethod
    def TestSenderHandle(cls): 

        cls.ResetAWS()

        cls.MOCKS().SYNCAPI().MockSyncApi('sender.com')
        cls.MOCKS().WEB().MockDomain('receiver.com')

        m = MSG({})
        m.RequireTo('receiver.com')
        m.RequireSubject("method@actor")

        e = m.Obj()
        cls.SENDER().Handle(e)
    

    # =====================================
    # RECEIVER
    # =====================================
    

    @classmethod
    def TestMap(cls): 
        
        cls.ResetAWS()

        method = 'method@actor'
        handler = 'any-lambda'

        cls.RECEIVER().MAP().New(
            subject= method,
            handler= handler)

        cls.AssertEqual(
            given= cls.RECEIVER().MAP().RequireMap(method).Handler(),
            expect= handler)
        

    @classmethod
    def TestReceiverHandle(cls): 
        
        # Initialize AWS.
        cls.ResetAWS()
        cls.MOCKS().SYNCAPI().MockHandler(
            domain= 'receiver.com',
            subject= 'method@actor')

        # Mock the message to be received.
        m = MSG({})
        m.RequireFrom('sender.com')
        m.RequireTo('receiver.com')
        m.RequireSubject('method@actor')
        m.Body({'A':1})
        m.Stamp()
        m.Sign(signature='<signature>', hash='<hash>')
        
        # Receive the event.
        r:str = cls.MOCKS().SYNCAPI().MockReceive(
            domain= 'receiver.com',
            event= m.Raw())
        
        # Validate the results.
        r = json.loads(r)
        ##cls.AssertEqual(r,{})
        ##cls.AssertNotEqual(r['statusCode'], 400)
        cls.AssertEqual(AWS_TEST.Echo['Body'], m['Body'])
    

    # =====================================
    # DKIM
    # =====================================


    @classmethod
    def TestValidateSignature(cls):

        cls.ResetAWS()

        cls.MOCKS().SYNCAPI().MockSyncApi()

        validator = cls.DKIM().ValidateSignature(
            text= 't',
            hash= '<hash>',
            publicKey= '<pk>',
            signature= '<signature>'
        )
        
        cls.AssertEqual(validator, {'hash': '<hash>', 'isVerified': True})
    

    @classmethod
    def TestHandleDkimCfn(cls):
        
        cls.ResetAWS()
        cls.MOCKS().ACTOR().MockActor()

        cls.MOCKS().SYNCAPI()._mockSyncApiDKIM()

        cls.DKIM().HandleDkimCfn()
          
        
    @classmethod
    def TestHandleKeyPairRotator(cls):
        
        cls.ResetAWS()
        cls.MOCKS().ACTOR().MockActor()

        cls.MOCKS().SYNCAPI()._mockSyncApiDKIM()

        cls.DKIM().HandleKeyPairRotator({})


    @classmethod
    def TestHandleSecretSetter(cls):

        cls.ResetAWS()
        
        # Set the key pair.
        cls.DKIM().HandleSecretSetter({
            "PublicKey": "pub",
            "PrivateKey": "priv"
        })

        # Verify
        cls.AssertEqual(cls.SENDER().PublicKey(), "pub")
        cls.AssertEqual(cls.SENDER().PrivateKey(), "priv")
        

    # =====================================
    # GLOBAL
    # =====================================


    @classmethod
    def TestSend(cls): 
        
        cls.ResetAWS()
        cls.MOCKS().SYNCAPI()._mockSyncApiSender('sender.com')
        cls.MOCKS().WEB().MockDomain('receiver.com')

        ret = cls.Invoke(
            to= 'receiver.com',
            subject= 'method@actor',
            body= {'A':1}
        )

        cls.AssertClass(ret, STRUCT)
        cls.AssertEqual(ret.Obj()['Body'], {'A':1})
        cls.AssertClass(ret.Obj(), dict)
    

    # =====================================
    # ALL TESTS
    # =====================================


    @classmethod
    def TestAllSyncAPI(cls): 
        LOG.Print('SYNCAPI_TESTS.TestAllSyncAPI() ==============================')

        # DKIM
        cls.TestValidateSignature()
        cls.TestHandleSecretSetter()
        cls.TestHandleDkimCfn()
        cls.TestHandleKeyPairRotator()

        # SENDER
        cls.TestSignMsg()
        cls.TestSenderHandle()

        # RECEIVER
        cls.TestMap()
        cls.TestReceiverHandle()

        # GLOBAL
        cls.TestSend()
       