from ISSUER import ISSUER
from PW_AWS.AWS_TEST import AWS_TEST


class ISSUER_MOCKS(ISSUER, AWS_TEST):


    @classmethod
    def MockIssuerSetup(cls, issuer, clean:bool):
        
        cls.MOCKS().VAULT().MockVault(
            vault= issuer,
            clean= clean)
        
        # Additional MSG handlers.
        cls.MOCKS(issuer).MESSENGER().MockHandlers(
            domain= issuer,
            ignoreValidation= False, 
            pairs= {
                'Accepted@Issuer': cls.HandleAccepted
            })

        # SYNCAPI handlers.
        cls.MOCKS().SYNCAPI().MockHandlers(
            domain= issuer,
            ignoreValidation=True, 
            pairs= {
                'Token@Issuer': cls.HandleToken,
            })
        

    @classmethod
    def MockIssuerConfig(cls,
                   issuer,
                   graph, 
                   clean:bool):
        
        cls.MOCKS().VAULT().MockVaultConfigs(
            vault= issuer,
            graph= graph,
            clean= clean)
        
    
    @classmethod
    def MockIssuerData(cls, issuer):

        cls.MOCKS().DYNAMO().MockTable(
            domain= issuer,
            table= 'SESSIONS',
            items= [{
                'ID': 'any-broker.org/<session-uuid>',
                'Broker': 'any-broker.org',
                'SessionID': '<session-uuid>'
            }]
        )

        cls.MOCKS().DYNAMO().MockTable(
            domain= issuer,
            table= 'BINDS',
            items= [{
                'ID': 'any-broker.org/<bind-uuid>',
                'Broker': 'any-broker.org',
                'BindID': '<bind-uuid>',
                'PublicKey': '<pk>'
            }]
        )

        cls.MOCKS().DYNAMO().MockTable(
            domain= issuer,
            table= 'TOKENS',
            items= [
                {
                    'ID': '<token-uuid>',
                    'Issuer': 'any-issuer.com',
                    'Broker': 'any-broker.org',
                    'SessionID': '<session-uuid>',
                    'QR': '<qr>',
                    'Code': 'any-authority.org/<code>',
                    'Revoked': False,
                    'Issued': '2023-04-01T05:00:30.001000Z',
                    'Starts': '2023-04-01T05:00:30.001000Z',
                    'Expires': '2123-04-01T05:00:30.001000Z',
                    'Version': '1.0.0'
                }, {
                    'ID': '<offer-uuid>',
                    'Issuer': 'any-issuer.com',
                    'Broker': 'any-broker.org',
                    'SessionID': '<session-uuid>',
                    'QR': '<qr>',
                    'Code': 'any-authority.org/<code>',
                    'Revoked': False,
                    'Issued': '2023-04-01T05:00:30.001000Z',
                    'Starts': '2023-04-01T05:00:30.001000Z',
                    'Expires': '2123-04-01T05:00:30.001000Z',
                    'Version': '1.0.0'
                }]
        )


    @classmethod
    def MockIssuer(cls,
                   issuer:str= 'any-issuer.com', 
                   graph:str= 'any-graph.com', 
                   clean:bool= False):
        
        cls.MockIssuerSetup(issuer=issuer, clean= clean)
        cls.MockIssuerConfig(issuer= issuer, graph=graph, clean=clean)

        if not clean:
            cls.MockIssuerData(issuer= issuer)
    
        cls.SetDomain(domain= issuer)