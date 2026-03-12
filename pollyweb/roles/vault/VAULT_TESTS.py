from VAULT import VAULT
from PW_AWS.AWS_TEST import AWS_TEST
from pollyweb import LOG


class VAULT_TESTS(VAULT, AWS_TEST):
        

    @classmethod
    def _handleBind(cls, event, outcomes):
        outcomes['VaultID'] = '<vaultID>'

    @classmethod
    def TestBound(cls):
        LOG.Print('VAULT_TESTS.TestBound() ==============================')

        cls.ResetAWS()
        cls.MOCKS().VAULT().MockVault()

        cls.OnPython(
            event= 'HandleBind@Vault', 
            handler= cls._handleBind)

        cls.HandleBound({
            "Header": {
                "From": "any-broker.org"
            },
            "Body": {
                "SessionID": "<session-uuid@vault>",
                "PublicKey": "pk",
                "Binds": [{
                    "ID": "793af21d-12b1-4cea-8b55-623a19a28fc5",
                    "Code": "airlines.any-igo.org/SSR/WCHR/CRED"
                }]
            }
        })
    

    @classmethod
    def TestContinue(cls):
        cls.ResetAWS()

        cls.HandleContinue({
            "Header": {
                "From": "any-broker.org"
            },
            "Body": {
                "Continue": "6704488d-fb53-446d-a52c-a567dac20d20"
            }
        })
    

    @classmethod
    def _onDisclose(cls, request):
        request['Data'] = '<user-data>'
        return request
    

    @classmethod
    def TestDisclose(cls):
        LOG.Print('VAULT_TESTS.TestDisclose() ==============================')

        broker = 'any-broker.org'
        vault = 'any-vault.org'
        consumer = 'any-consumer.org'

        cls.ResetAWS()

        cls.MOCKS().CONSUMER().MockConsumer()

        cls.MOCKS().VAULT().MockVault()     

        cls.MOCKS().HANDLER().MockLambdaHandler(
            domain= vault,
            event= 'OnDisclose@Vault',
            handler= cls._onDisclose
        )   
 
        cls.SetDomain(vault)
        cls.HandleDisclose({
            "Header": {
                "From": broker,
                "To": vault,
                "Subject": "Disclose@Vault"
            },
            "Body": {
                "SessionID": "<session-uuid@consumer>",
                "Consumer": consumer,
                "Language": "en-us",
                "BindID": "<bind-uuid>"
            },
            "Hash": "<hash>",
            "Signature": "<signature>"
        })


    @classmethod
    def TestSuppress(cls):
        LOG.Print('VAULT_TESTS.TestSuppress() ==============================')

        vault = 'any-vault.org'

        cls.ResetAWS(vault)

        cls.MOCKS(vault).VAULT().MockVault(vault)
        cls.MOCKS(vault).DYNAMO('SESSIONS').MatchCount(1)

        cls.HandleSuppress({
            "Header": {
                "From": "any-broker.org"
            },
            "Body": {
                "Consumer": "airline.any-business.org",
                "SessionID": "<session-uuid@vault>"
            }
        })


    @classmethod
    def TestUnbind(cls):
        LOG.Print('VAULT_TESTS.TestUnbind() ==============================')
        
        vault = 'any-vault.org'

        cls.ResetAWS(domain= vault)

        cls.MOCKS().DYNAMO().MockTable(
            domain= vault,
            table= 'BINDS',
            items= [{
                'ID': 'any-broker.org/<bind-uuid>',
                'PublicKey': '<pk>',
                'Code': 'any-authority.org/<code>'
            }])
        
        cls.HandleUnbind({
            "Header": {
                "From": "any-broker.org"
            },
            "Body": {
                "BindID": "<bind-uuid>"
            }
        })
    

    @classmethod
    def TestAllVault(cls):
        LOG.Print('VAULT_TESTS.TestAllVault() ==============================')

        cls.TestBound()
        #cls.TestContinue()
        cls.TestDisclose()
        cls.TestSuppress()
        cls.TestUnbind()
