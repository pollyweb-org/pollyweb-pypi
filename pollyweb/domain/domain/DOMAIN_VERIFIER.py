from PW_AWS.AWS import AWS
from PW_AWS.DEPLOYER_EXEC_LAMBDA import DEPLOYER_EXEC_LAMBDA
from pollyweb import LOG
from pollyweb import TESTS


class DOMAIN_VERIFIER():


    def VerifyBackUp(self, event:DEPLOYER_EXEC_LAMBDA):
        event.InvokeLambda({})

    
    def VerifyRetireLayers(self, event:DEPLOYER_EXEC_LAMBDA):
        event.InvokeLambda({})


    def VerifyGenerator(self, event:DEPLOYER_EXEC_LAMBDA):
        result = event.InvokeLambda({})
        result.Require()
        result.RequireStr('PrivateKey')
        result.RequireStr('PublicKey')


    def VerifySecretSetter(self, event:DEPLOYER_EXEC_LAMBDA):
        pri = "my-private-key"
        pub = "my-public-key"
        
        event.InvokeLambda({
            "PublicKey": pub,
            "PrivateKey": pri
        })
        
        secrets = AWS.SECRETS()
        TESTS.AssertEqual(pub, secrets.Get('/PW/PublicKey').GetValue())
        TESTS.AssertEqual(pri, secrets.Get('/PW/PrivateKey').GetValue())
        

    def VerifyRotator(self, event:DEPLOYER_EXEC_LAMBDA):
        LOG.Print('@', event)
        event.InvokeLambda({})
        LOG.RaiseException('Should have raised an exception')


    def VerifyAlerter(self, event:DEPLOYER_EXEC_LAMBDA):
        LOG.Print('@', event)
        event.InvokeLambda({
            "Type": "OnDeploymentComplete"
        })
