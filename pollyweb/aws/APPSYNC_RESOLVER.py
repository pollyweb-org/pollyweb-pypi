# 📚 APPSYNC
# FROM: https://dev.to/trisduong/tutorial-use-aws-eventbridge-and-appsync-for-real-time-notification-to-client-side-405a


from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT


class APPSYNC_RESOLVER:
        

    @classmethod
    def Arguments(cls, event:dict):
        return STRUCT(event).RequireStr('arguments')
    

    @classmethod
    def UserName(cls, event:dict):
        return STRUCT(event).RequireStr('context.identity.username')