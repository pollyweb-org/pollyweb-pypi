# 🤝 PW

from PW_INTERFACES import PW_INTERFACES
from PW_BEHAVIORS import PW_BEHAVIORS
from PW_ROLES import PW_ROLES


# ✅ DONE
class PW:
    ''' 🤝 Domain Trust Framework.
    Docs: https://quip.com/z095AywlrA82/-Domain-Trust-Framework '''
    
    
    @classmethod
    def BEHAVIORS(cls):
        '''👉 List of behaviors of PW Actors.'''
        return PW_BEHAVIORS()


    @classmethod
    def CONFIG(cls):
        ''' 👉 Settings stored on DynamoDB. '''
        from CONFIG import CONFIG as proxy
        return proxy()
    

    @classmethod
    def INTERFACES(cls):
        return PW_INTERFACES()


    @classmethod
    def AWS(cls):
        ''' 👉 AWS Helpers. '''
        from PW_AWS.AWS import AWS as proxy
        return proxy()
    
    
    @classmethod
    def ROLES(cls):
        '''👉 List of roles of PW Actors.'''
        return PW_ROLES()
    
    
    @classmethod
    def UTILS(cls):
        '''👉️ Generic methods.'''
        from pollyweb import UTILS as proxy
        return proxy()


    @classmethod
    def DEPLOY(cls):
        '''👉️ Deployment tools. '''
        from DEPLOY import DEPLOY as proxy
        return proxy()
    

    @classmethod
    def DOMAIN(cls, name:str=None):
        ''' 👥 Wrapper of a domain. '''
        from DOMAIN import DOMAIN as proxy
        if name:
            return proxy(name)
        else:
            return proxy()
    
    
    @classmethod
    def WALLET(cls):
        from WALLET import WALLET as proxy
        return proxy.GetWallet()
    

