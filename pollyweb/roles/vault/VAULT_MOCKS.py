from PW_AWS.AWS_TEST import AWS_TEST
from VAULT import VAULT
from HOST_MOCKS import HOST_MOCKS
from pollyweb import UTILS


class VAULT_MOCKS(VAULT, HOST_MOCKS, AWS_TEST):
        

    @classmethod
    def MockVaultSetup(cls, vault:str, clean:bool):
        
        # HOST handlers.
        cls.MOCKS(vault).HOST().MockHostSetup(
            host= vault,
            clean= clean)
                    
        # Additional MSG handlers.
        cls.MOCKS(vault).MESSENGER().MockHandlers(
            domain= vault,
            ignoreValidation= False, 
            pairs= {
                'Bound@Vault': cls.HandleBound,
                'Continue@Vault': cls.HandleContinue,
                'Disclose@Vault': cls.HandleDisclose,
                'Suppress@Vault': cls.HandleSuppress,
                'Unbind@Vault': cls.HandleUnbind
            })
        
        # Additional HANDLER handlers.
        cls.MOCKS(vault).HANDLER().RegisterLambdaHandlers(
            events= [
                'OnDisclose@Vault',
                'OnSupress@Vault',
                'OnBound@Vault'
            ])


    @classmethod
    def MockVaultConfigs(cls, 
                         vault:str, 
                         graph:str,
                         clean:bool):
        
        if clean != True:
            # Mock a GRAPH.
            cls.MOCKS(graph).GRAPH().MockGraph(
                graph= graph,
                manifest= vault)

        # Config HOST settings.
        cls.MOCKS(vault).HOST().MockHostConfigs(
            host= vault,
            graph= graph,
            clean= clean)
        
        if clean != True:
            cls.MOCKS().HANDLER().MockLambdaHandler(
                domain= vault,
                event= 'OnBound@Vault', 
                handler= lambda x: { 
                    'VaultID': '<vaultID>', 
                    'Confirmed': True 
                })
        
        if clean != True:
            cls.MOCKS().HANDLER().MockLambdaHandler(
                domain= vault,
                event= 'OnDisclose@Vault', 
                handler= lambda x: {
                    'Version': '1.0.0',
                    'Data': '<user-data>'
                })


    @classmethod
    def MockSessions(cls, vault:str, clean:bool):

        # SESSIONS table.
        if not clean:
            cls.MOCKS().DYNAMO().MockTable(
                domain= vault,
                table= 'SESSIONS',
                items=[{
                    "ID": "any-broker.org/<session-uuid@vault>",
                    "SessionID": "<session-uuid@vault>"
                }])
        
        # BINDS table.
        if not clean:
            cls.MOCKS().DYNAMO().MockTable(
                domain= vault,
                table= 'BINDS',
                items=[{
                    "ID": "any-broker.org/<bind-uuid>",
                    "PublicKey": "<pk>",
                    'Code': 'any-authority.org/<code>'
                }])


    @classmethod
    def MockVault(cls, 
                  vault:str='any-vault.org', 
                  graph:str='any-graph.com',
                  clean:bool= False
                  ) -> str:
        
        cls.SetDomain(vault)
        
        if cls.IsDomainMocked(domain=vault, component=cls):
            return
        
        if clean != True:
            cls.MOCKS().GRAPH().MockGraph(
                graph= graph, 
                manifest= vault)
        
        cls.MockVaultSetup(
            vault= vault,
            clean= clean)
        
        cls.MockVaultConfigs(
            vault= vault, 
            graph= graph,
            clean= clean)
        
        if clean != True:
            cls.MockSessions(
                vault= vault, 
                clean= clean)

        cls.SetDomain(vault)
        return vault