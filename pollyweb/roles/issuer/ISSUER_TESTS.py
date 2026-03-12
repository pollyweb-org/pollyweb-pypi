from pollyweb import UTILS
from PW_AWS.AWS import AWS
from pollyweb import STRUCT
from PW import PW
from SESSION import SESSION
from MSG import MSG

from ISSUER import ISSUER
from PW_AWS.AWS_TEST import AWS_TEST
from ISSUER_MOCKS import ISSUER_MOCKS

class ISSUER_TESTS(ISSUER_MOCKS, ISSUER, AWS_TEST):
    

    @classmethod
    def TestToken(cls):
        cls.ResetAWS()

        cls.MockIssuer()

        ret = cls.HandleToken({
            "Header": {
                "From": "any-broker.org",
                "To": "any-issuer.com",
                "Subject": "Token@Issuer"
            },
            "Body": {
                "SessionID": "<session-uuid>",
                "TokenID": "<token-uuid>"
            },
            "Hash": "<hash>",
            "Signature": "<signature>"
        })

        cls.AssertEqual(ret, {
            'QR': '<qr>'
        })


    @classmethod
    def TestStatus(cls):
        cls.ResetAWS()

        cls.MockIssuer()

        cls.HandleStatus({
            "Header": {
                "From": "any-broker.org",
                "To": "any-issuer.com",
                "Subject": "Token@Issuer"
            },
            "Body": {
                "Locator": "<token-uuid>"
            },
            "Hash": "<hash>",
            "Signature": "<signature>"
        })
    

    @classmethod
    def TestIssue(cls):
        cls.ResetAWS()
        cls.MockIssuer()

        ret = cls.Issue(
            broker= 'any-broker.org',
            code= 'authority.com/<code>',
            version= '1.0',
            sessionID= '<session-uuid>',
            starts= '2023-04-01T05:00:30.001000Z',
            expires= '2123-04-01T05:00:30.001000Z'
        )

        cls.AssertEqual(ret['Code'], 'authority.com/<code>')


    @classmethod
    def TestOffer(cls):
        cls.ResetAWS()

        cls.MOCKS().BROKER().MockBroker(host='any-issuer.com')
        cls.MOCKS().ISSUER().MockIssuer()
        
        cls.Offer(
            source= 'ISSUER_TESTS',
            session= SESSION.New(
                host= 'any-host.org',
                locator= '<locator>',
                broker= 'any-broker.org',
                sessionID= '<session-uuid>'),
            code= 'any-authority.org/<code>',
            tokenID= '<token-uuid>')
    

    @classmethod
    def TestRevoke(cls):
        cls.ResetAWS()

        cls.MOCKS().BROKER().MockBroker(host='any-issuer.com')
        cls.MOCKS().ISSUER().MockIssuer()

        cls.Revoke(
            source= 'ISSUER_TESTS',
            session= SESSION.New(
                host= 'any-host.org',
                locator= '<locator>',
                broker= 'any-broker.org',
                sessionID= '<session-uuid>'),
            tokenID= '<token-uuid>')


    @classmethod
    def TestAllIssuer(cls):
        cls.TestToken()
        cls.TestStatus()
        cls.TestIssue()
        cls.TestOffer()
        cls.TestRevoke()