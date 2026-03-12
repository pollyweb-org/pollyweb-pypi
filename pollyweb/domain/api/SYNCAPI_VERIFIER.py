from PW_AWS.DEPLOYER_EXEC_LAMBDA import DEPLOYER_EXEC_LAMBDA
from pollyweb import LOG
from SYNCAPI import SYNCAPI
from MSG import MSG
from pollyweb import TESTS


class SYNCAPI_VERIFIER(SYNCAPI):

    
    def __init__(self) -> None:
        self.text = "{\"Header\":{\"Correlation\":\"bb37d258-015c-497e-8a67-50bf244a9299\",\"Timestamp\":\"2023-06-24T23:08:24.550719Z\",\"To\":\"105b4478-eaa5-4b73-b2a5-4da2c3c2dac0.dev.pollyweb.org\",\"Subject\":\"AnyMethod\",\"Code\":\"pollyweb.org/msg\",\"Version\":\"1\",\"From\":\"105b4478-eaa5-4b73-b2a5-4da2c3c2dac0.dev.pollyweb.org\"},\"Body\":{}}"
        self.hash = "ee6ca2a43ec05d0bd855803407b9350e6c84dd1b981274e51ce0a0a8be16e4a1"
        self.algorithm = "SHA256"
        self.privateKey = "-----BEGIN RSA P{REMOVE-GIT}RIVATE KEY-----\nMIIEpAIBAAKCAQEAu6BtCd1lWxCxmddGMIqxivaRjp4AO/PriDWA6ZIyk20I4bjc\nvcl6qAgj4VeuvRx+qBkmZ1hRu0j87fBPYm7XiGQsvLJ2ctG3XeddWRH5DWxnR3tM\nObQvYIAGwoV8hetNyQLBSBGPzgkGyhGXoLGyY7CfjQaiR8TDLqiZZG1MPIPmbJds\n1DeT+vYIsKH7OQymcPg1yTZMAdoBsYuisEN/tVoTsLQY9qXkJSS99li9W7AcNKIP\nBtz9gG0A3ZQKnO7NjZc/f+Seb0h0SMjPMrmBC88NRQqId2znKtALawXdp6yLe5IL\n1M/rUVIHLqs2hZEDjH++3ZNm4AUO7co8MTmscQIDAQABAoIBAA5y2g1r7LhjY+He\nd5ZuX8y9PylLQTuyBX3Nl6SlBbBfsag8RazMfV2/lA/FjPxy23gTc7x6oH9P2BZ0\nrpBRy9bs1pseEna2Gqz9ule3xW+YslK0C9iCZ9xCZQLe0l+NEXDnfZM7XaZ2qydY\nInk/+zunvX8CjJsCloCbKtuBJTagVHnxPIuDGtA5bSv4QhGbKEbSBN5X1KA/HAYj\nHl4CNAMZpz1eqkQupzXzBt557BuIsK7VTx2M6wXIRzY7QgZVzE4zouqgHHT09Lp+\n0W4xjmYSuCHfZ/8cC6ZpQW5bxsQQUv9ioW3Xr7nX2pnPs/3ypFrXp/c1H99tQhf0\nYVmRvakCgYEAyfGvht0JlaVhuRjUYbNQFMgQzH+VQzepinMDtbM/m4NcdVEza8V7\ngoQahWRSIHJM9vDpQoCuLVKNr0RVYNwcLyOr4RpBfWLwa0ExUDyRj7fYsp913yUv\nuG2hWFunmmaKLDqearVcoC5veLLGAQHBwCPX4QqRtW/LJ3ULaKUFwpUCgYEA7dmh\n2Q9zzugg1SGo9RzxxuE4C7lf0hRAqsj+gwasumQbYHzPPhHuew/4vRJ0dBJomrmq\ng5bCfracgYQnOUHzry2nGp2Eia6GMad/5U6NogessO8AxW40A3kOJF+ljwUn7op2\nYdYje56KK9uj2f/iY13EJ8VoY9f4BR42Fyh0x20CgYEAo2Vlk6aXUbjd6Cl59o9i\ntV3nkb+NYzTPflFvZ/5f8hGIpvgLtiC0vbbrypCQjuZM9eWZpxB9XfiU4YJV3qha\nOZ4QPXPEF5MNWosGPpizYmjr8iNp+SKaiQxTZy3J3/klxYGsmkSibI0F7tAfu8LT\nJQcbbl/h479Pzl462/HiRj0CgYAiwPINLVzWlsR1X/24Ewqg7LervuJpZ9wrGENY\nEdmbQpVde98sSqJ2CNdniRLLAwWV1hs8LwMsULJ9mjnA/AoHRrxr/ygmlgG1r6vY\nban0SvrIv6N1Na0T9NRELFWcmDxFdqXllcyJe5jk36sJZ4JE0qaeyRF/xUbQOKHe\nsGKf4QKBgQCeJR1IslIsjFhaa8hsOXI0K/bJGIt+IOuECq4sy8RH51zF1x7YR51P\nNAq+3F9PYDJE+LjkqQALZZYEaiBruPSdRfqXvEOrrnC1koB+gBFD27ABeQASqRvm\nRTqj7Zw9UOmFZDdDUcEwFuM7Bu0O9UTm3f2zsKsnFwLon3mvazhMmw==\n-----END RSA PRIVATE KEY-----\n"
        self.publicKey = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu6BtCd1lWxCxmddGMIqx\nivaRjp4AO/PriDWA6ZIyk20I4bjcvcl6qAgj4VeuvRx+qBkmZ1hRu0j87fBPYm7X\niGQsvLJ2ctG3XeddWRH5DWxnR3tMObQvYIAGwoV8hetNyQLBSBGPzgkGyhGXoLGy\nY7CfjQaiR8TDLqiZZG1MPIPmbJds1DeT+vYIsKH7OQymcPg1yTZMAdoBsYuisEN/\ntVoTsLQY9qXkJSS99li9W7AcNKIPBtz9gG0A3ZQKnO7NjZc/f+Seb0h0SMjPMrmB\nC88NRQqId2znKtALawXdp6yLe5IL1M/rUVIHLqs2hZEDjH++3ZNm4AUO7co8MTms\ncQIDAQAB\n-----END PUBLIC KEY-----\n"
        self.signature = "q0HOEhUSyk1g/6TZEF2v6uWxkP0OdwdKGin5EnW/pBfbOY2ke3pyajJGaN8doZwDqiASlLqEgapur7j1Rv/XCM3PdH/9hkE4y0w2QfdkHIApEBPlX+TQAK51ACiC07O2qi3rM5czZiOLWEmjpqa54A0q6C2wFdzEGqiahNWY6MR5v2oYE5Va5P840gjXSBggktJQW1YCAbDg4EXscHt6fPv49PAV9/YK50oaHUE/TbSQHDf9RsJCCEIrhMg81ojQK35YZ+KVOmqwpwaSzUGvr6KJXrzSYvoP867m8zajaeC7fU0PH49VGRwZEYCmc7hCo21hGIYfv+MwinvEmjTcAw=="
        self.isVerified: True


    def VerifyValidator(self, task:DEPLOYER_EXEC_LAMBDA):

        TESTS.AssertEqual(
            task.InvokeLambda({
                'text': self.text,
                'publicKey': self.publicKey,
                'signature': self.signature
            }), {
                'hash': self.hash, 
                'isVerified': True
            })

        validator = SYNCAPI.DKIM().ValidateSignature(
            text= self.text,
            hash= self.hash,
            publicKey= self.publicKey,
            signature= self.signature)
        
        TESTS.AssertEqual(
            validator, 
            {
                'hash': self.hash, 
                'isVerified': True
            })
        
        validator = SYNCAPI.DKIM().ValidateSignature(
            text= self.text,
            hash= self.hash,
            publicKey= self.publicKey,
            signature= 'something-else')
        
        TESTS.AssertEqual(
            validator, {
                'hash': self.hash, 
                'isVerified': False
            })
        
        LOG.Print('Nice, DKIM validation worked!')


    def VerifySigner(self, event:DEPLOYER_EXEC_LAMBDA):
        ''' 👉️ Signs a dummy message and verifies the signature'''
        
        import os
        os.environ['VALIDATOR'] = 'SyncApiDkim-Validator'

        # Create a dummy message.
        msg = MSG({})
        msg.RequireTo('any-domain.com')
        
        # Sign the dummy message.
        SYNCAPI.SENDER().SignMsg(
            privateKey= self.privateKey, 
            publicKey= self.publicKey, 
            msg= msg)
        
        # Verify the signature.
        msg.VerifySignature(
            publicKey= self.publicKey)
        

    def VerifyDkimReader(self, task:DEPLOYER_EXEC_LAMBDA):
        ret = task.InvokeLambda({
            "hostname": "pollyweb._domainkey.pollyweb.org"
        })
        
        if ret == 'NOT FOUND!':
            LOG.RaiseValidationException('DKIM record found!')
        
        # The DKIM record is expected to be this one as of 2024/Aug/10.
        if ret != "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAskGYC2P1fXI+mPVHA+mjIE+DEjAKwQcJFkKRSNh6ouaiVn5p2xxZZwp6RdRyLgU55jcXKpUo3LaS4DashNf8ylbZoVTSjV6rRBmB+RCyrP0TYPxyCEbY9F8+pqDSOne/HrJBC4mj9y0/dnclRgwIXALfcFKvgRIoZk1Q3jvWgMWbp9hyeE4V7gfOP1v8syiVh9Qc1atBO1vAR4p01ycHwltPtW3YA/UGwN7vVdW9F91QTzQ0ri89TTHB9Snvwy6YmRAezAVEYJf4QXJG3z8nslc9cVlymthAljtptELJeFYQuCfNnMYkZcuGSEW8PsQAF02n6Pe8PigQdv9/MGGmCwIDAQAB":
            LOG.RaiseValidationException('Unexpected DKIM!')

        


    def VerifySender(self, task:DEPLOYER_EXEC_LAMBDA): 
        pass
