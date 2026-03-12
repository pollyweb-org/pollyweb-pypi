# 📚 ACTOR


# ✅ DONE
class ACTOR():
    ''' 🤝 Actor in Domain Trust Framework.'''
    

    @classmethod
    def AWS(cls):
        ''' 👉 Link to AWS Helpers. '''
        from PW_AWS.AWS import AWS as proxy
        return proxy()
    

    @classmethod
    def PW(cls):
        ''' 🤝 Domain Trust Framework.'''
        from PW import PW as proxy
        return proxy()
    

    @classmethod
    def UTILS(cls):
        '''👉️ Generic methods.'''
        from pollyweb import UTILS as proxy
        return proxy()
    
    
    @classmethod
    def WEB(cls):
        ''' 🤝 Web Utils.'''
        from WEB import WEB as proxy
        return proxy()
    
    