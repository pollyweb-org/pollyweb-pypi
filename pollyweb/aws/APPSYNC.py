# 📚 APPSYNC
   
class APPSYNC():
        
    @classmethod
    def CLIENT(cls, ApiUrl:str, ApiKey:str):
        from APPSYNC_CLIENT import APPSYNC_CLIENT as proxy
        return proxy(API_URL=ApiUrl, API_KEY=ApiKey)
    

    @classmethod
    def RESOLVER():
        from APPSYNC_RESOLVER import APPSYNC_RESOLVER as proxy
        return proxy()
