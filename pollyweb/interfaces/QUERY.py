from ..utils import UTILS
from ..utils import STRUCT
from .CODE import CODE
from ..utils import LOG


class CONSUMER_QUERY(STRUCT):
    '''
    Example: 
    {
        "Code": "airlines.any-igo.org/SSR/*",
        "Message": "Let's handle your special requests.",
        "Vaults": ["ec.europa.eu"]
    }
    '''
    
        
    @classmethod
    def New(cls, code:str, message:str):
        
        UTILS.RequireArgs([code, message])
        CODE.Verify(code)
        
        ret = CONSUMER_QUERY({
            'Code': code,
            'Message': message
        })
        
        ret.VerifyConsumerQuery()
        return ret
    

    def RequireCode(self):
        '''👉 Code of the schema of the info to be disclosed.'''
        return self.RequireStr('Code')
    
    
    def RequireMessage(self):
        '''👉 Message justifying the need for the sharing of the code.'''
        return self.RequireStr('Message')
        

    def VerifyConsumerQuery(self):
        '''👉 Verifies if all required properties are set.'''

        self.Require()
        self.RequireMessage()
        
        code = self.RequireCode()
        CODE.Verify(code)
    

    def IncludesCode(self, code:str):
        '''👉 Indicates of the code is part of the requested set of codes to be disclosed.'''
        
        queriedCode = self.RequireCode()

        # Look for an exact match.
        if code == queriedCode:
            return True
        
        # Look for a wildcard at the end, e.g. airlines.any-igo.org/SSR/*
        if queriedCode.endswith('*'):
            prefix = queriedCode.replace('*', '')
            if code.startswith(prefix):
                return True
                
        return False
    


class BROKER_QUERY(STRUCT):
    '''
    Queriable example: 
    {
        "Code": "airlines.any-igo.org/SSR/*",
        "Message": "Let's handle your special requests.",
        "Translation": "Wheelchair assistance required",
        "Queryable": True,
        "Binds": [{
            "Vault": "ec.europa.eu",
            "Translation": "European Union",
            "BindID": "1313c5c6-4038-44ea-815b-73d244eda85e"
        }],
        "Tokens": [{
            "Issuer": "ec.europa.eu",
            "Translation": "European Union",
            "TokenID": "1313c5c6-4038-44ea-815b-73d244eda85e",
            "Version": "1.0.0",
            "Path": "/storage/tokens/1313c5c6-4038-44ea-815b-73d244eda85e.txt"
        }]
    }

    Non-queriable example: 
    {
        "Code": "airlines.any-igo.org/SSR/*",
        "Message": "Let's handle your special requests.",
        "Translation": "Wheelchair assistance required",
        "Queriable": False,
        "Binds": [],
        "Tokens": []
    }
    '''

    @staticmethod 
    def New(query: CONSUMER_QUERY, 
            translation:str, 
            tokens: list[any],
            binds: list[any]):
        
        # Match classes.
        UTILS.AssertIsType(query, CONSUMER_QUERY)
        UTILS.AssertIsType(tokens, list)
        
        # Find duplicates.
        UTILS.VerifyDuplicates(binds)
        UTILS.VerifyDuplicates(tokens)

        # It's queriable if it has at least 1 bind or 1 token.
        queryable = len(binds+tokens) > 0

        ret = BROKER_QUERY({
            'Code': query.RequireCode(),
            'Message': query.RequireMessage(),
            'Queryable': queryable,
            'Translation': translation,
            'Binds': binds,
            'Tokens': tokens
        })

        ret.VerifyBrokerQuery()
        return ret

    
    def RequireCode(self):
        '''👉 Code of the schema of the info to be disclosed.'''
        return self.RequireStr('Code')
    
    def RequireMessage(self):
        '''👉 Message justifying the need for the sharing of the code.'''
        return self.RequireStr('Message')

    def RequireQueryable(self):
        return self.RequireBool('Queryable')
    
    def RequireTranslation(self):
        return self.RequireStr('Translation')
        
    def RequireBinds(self):
        return [STRUCT(b) for b in self.GetList('Binds', mustExits=True)]
    
    def RequireTokens(self):
        return [STRUCT(c) for c in self.GetList('Tokens', mustExits=True)]
    

    def VerifyBrokerQuery(self):
        '''👉 Verifies if all required properties are set.'''

        LOG.Print(f'📡✅ QUERY.VerifyBrokerQuery()', self)

        self.Require()
        self.RequireMessage()
        
        code = self.RequireCode()
        CODE.Verify(code)

        self.RequireTranslation()
        self.RequireQueryable()

        # If queriable, then binds or tokens should have values.
        if self.RequireQueryable() == True:
            queryable:list = self.RequireBinds() + self.RequireTokens()
            UTILS.Require(queryable, 
                msg='Given is queryable, is there at least 1 bind or token?')
            
        # If not queriable, then binds and tokens should be empty.
        if self.RequireQueryable() == False:
            UTILS.AssertLenght(self.RequireBinds(), 0)
            UTILS.AssertLenght(self.RequireTokens(), 0)

        # Binds
        UTILS.VerifyDuplicates(self.RequireBinds())
        for bind in self.RequireBinds():
            bind.RequireStr('Vault')
            bind.RequireStr('Translation')
            bind.RequireUUID('BindID')
            bind.GetList('Trusts', mustExits=True)
            
        # Tokens
        UTILS.VerifyDuplicates(self.RequireTokens())
        for token in self.RequireTokens():
            token.RequireStr('Issuer')
            token.RequireStr('Translation')
            token.RequireUUID('TokenID')
            token.RequireStr('Version')
            token.RequireStr('Path')
            token.RequireTimestamp('Starts')
            token.GetTimestamp('Expires')
            token.GetList('Trusts', mustExits=True)

        # Vaults (ensure the message was not copied from the consumer).
        if self.ContainsAtt('Vaults'):
            LOG.RaiseException('Vaults should not be in the query!')
        
        # Tokens should not apper in binds.
        for token in self.RequireTokens():
            for bind in self.RequireBinds():
                vault = bind.RequireStr('Vault')
                issuer = token.RequireStr('Issuer')
                if vault == issuer:
                    LOG.RaiseException(f'Issuer=({issuer}) should not be in binds! Please remove.')


    def RequireBind(self, vault:str):
        UTILS.Require(
            self.RequireBinds(),
            msg=f'QUERY.Bind({vault}): The broker sent no binds in query={self.Raw()}?')
        
        bind = STRUCT(self.RequireBinds()).First('Vault', equals= vault)
        bind.RequireAtt(msg=f'Bind found for vault=({vault}) in brokers query={self.Raw()}?')

        return bind