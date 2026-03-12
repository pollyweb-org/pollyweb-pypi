# 🤝 PW


class PW_BEHAVIORS:


    @classmethod
    def CRUD(cls):
        ''' 👉 Data model with custom tables. '''
        from CRUD import CRUD as proxy
        return proxy()

    
    @classmethod
    def HANDLER(cls):
        ''' 👉 Registers and triggers code events. '''
        from PW_UTILS.HANDLER import HANDLER as proxy
        return proxy()
    
    
    @classmethod
    def MANIFESTER(cls):
        ''' 👉️ Sends manifest updates to a listener.'''
        from MANIFESTER import MANIFESTER as proxy
        return proxy()
    
    
    @classmethod
    def MESSENGER(cls):
        ''' 👉 Messenger behaviour of a domain. '''
        from MESSENGER import MESSENGER as proxy
        return proxy()


    @classmethod
    def PUBLISHER(cls):
        ''' 📤 Publisher: https://quip.com/sBavA8QtRpXu/-Publisher '''
        from PUBLISHER import PUBLISHER as proxy
        return proxy()


    @classmethod
    def SUBSCRIBER(cls):
        ''' 📥 Subscriber: https://quip.com/9ab7AO56kkxY/-Subscriber '''
        from SUBSCRIBER import SUBSCRIBER as proxy
        return proxy()


    @classmethod
    def SYNCAPI(cls):
        from SYNCAPI import SYNCAPI as proxy
        return proxy()
    
    @classmethod
    def TALKER(cls):
        from TALKER import TALKER as proxy
        return proxy()
    
    
    @classmethod
    def TRANSFER(cls):
        '''👉 Allows for 2 domains to securily transfer files between each other
        without adding the content of the file to the requests.'''
        from TRANSFER import TRANSFER as proxy
        return proxy()


