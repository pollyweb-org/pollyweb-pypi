# 🤝 PW


class PW_ROLES:
    

    @classmethod
    def BROKER(cls):
        ''' 🤵 https://quip.com/SJadAQ8syGP0/-Broker '''
        from BROKER import BROKER as proxy
        return proxy()
    
    @classmethod
    def BUYER(cls):
        '''👉 Actor that sends orders to suppliers.'''
        from BUYER import BUYER as proxy
        return proxy()
    
    @classmethod
    def COLLECTOR(cls):
        from COLLECTOR import COLLECTOR as proxy
        return proxy()

    @classmethod
    def CONSUMER(cls):
        ''' 📡 https://quip.com/UbokAEferibV/-Consumer '''
        from CONSUMER import CONSUMER as proxy
        return proxy()

    @classmethod
    def DATASET(cls):
        '''👉 Actor that exposes dataset.'''
        from DATASET import DATASET as proxy
        return proxy()
    
    @classmethod
    def EPHEMERAL_BUYER(cls):
        from EPHEMERAL_BUYER import EPHEMERAL_BUYER as proxy
        return proxy()
    

    @classmethod
    def EPHEMERAL_SUPPLIER(cls):
        from EPHEMERAL_SUPPLIER import EPHEMERAL_SUPPLIER as proxy
        return proxy()


    @classmethod
    def GRAPH(cls):
        '''👉 Actor that provides trust paths and translations.'''
        from GRAPH import GRAPH as proxy
        return proxy()
    

    @classmethod
    def HOST(cls):
        '''👉 Actor that holds users sessions.'''
        from HOST import HOST as proxy
        return proxy()
    

    @classmethod
    def ISSUER(cls):
        '''👉 Actor that issues tokens.'''
        from ISSUER import ISSUER as proxy
        return proxy()


    @classmethod
    def LISTENER(listener):
        '''👉 Actor that listens to updates of domain manifests.'''
        from LISTENER import LISTENER as proxy
        return proxy()


    @classmethod
    def NOTIFIER(cls):
        ''' 📣 Notifier: https://quip.com/PCunAKUqSObO/-Notifier '''
        from NOTIFIER import NOTIFIER as proxy
        return proxy()


    @classmethod
    def PALMIST(cls):
        from PALMIST import PALMIST as proxy
        return proxy()


    @classmethod
    def PAYER(cls):
        from PAYER import PAYER as proxy
        return proxy()


    @classmethod
    def PRINTER(cls):
        from PRINTER import PRINTER as proxy
        return proxy()


    @classmethod
    def SELFIE_BUYER(cls):
        from SELFIE_BUYER import SELFIE_BUYER as proxy
        return proxy()


    @classmethod
    def SELFIE_SUPPLIER(cls):
        from SELFIE_SUPPLIER import SELFIE_SUPPLIER as proxy
        return proxy()
    

    @classmethod
    def SELLER(cls):
        from SELLER import SELLER as proxy
        return proxy()
    

    @classmethod
    def SUPPLIER(cls):
        '''👉️ Fulfils orders sent by buyers.'''
        from SUPPLIER import SUPPLIER as proxy
        return proxy()


    @classmethod
    def TRANSCRIBER_BUYER(cls):
        from TRANSCRIBER_BUYER import TRANSCRIBER_BUYER as proxy
        return proxy()
    

    @classmethod
    def TRANSCRIBER_SUPPLIER(cls):
        from TRANSCRIBER_SUPPLIER import TRANSCRIBER_SUPPLIER as proxy
        return proxy()


    @classmethod
    def VAULT(cls):
        '''🗄️ Holds user secrets.'''
        from VAULT import VAULT as proxy
        return proxy()


    @classmethod
    def WIFI(cls):
        from WIFI import WIFI as proxy
        return proxy()
    

# ✅ DONE
class PW:
    ''' 🤝 Domain Trust Framework.
    Docs: https://quip.com/z095AywlrA82/-Domain-Trust-Framework '''
    
    
    @classmethod
    def BEHAVIOURS(cls):
        '''👉 List of behaviours of PW Actors.'''
        return PW_BEHAVIOURS()

    @classmethod
    def INTERFACES(cls):
        return PW_INTERFACES()

    @classmethod
    def CONFIG(cls):
        ''' 👉 Settings stored on DynamoDB. '''
        from CONFIG import CONFIG as proxy
        return proxy()

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
    def DOMAIN(cls, name:str=None):
        ''' 👥 Wrapper of a domain. '''
        from DOMAIN import DOMAIN as proxy
        return proxy(name)
    
    @classmethod
    def WALLET(cls):
        from WALLET import WALLET as proxy
        return proxy.GetWallet()
    

