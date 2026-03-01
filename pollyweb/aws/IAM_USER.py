# 📚 STS

from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT

class IAM_USER(STRUCT):
    '''👉️ Represents the logged user.'''
    
    def __init__(self, user:dict) -> None:
        '''👉️ Initializes the user.'''
        super().__init__(user)


    def RequireUserName(self):
        '''👉️ Returns the user name.'''
        return self.RequireStr('UserName')
    

    def RequireArn(self):
        '''👉️ Returns the user ARN.'''
        return self.RequireStr('Arn')
    

    def RequireAccount(self):
        '''👉️ Returns the user account.'''
        # Given "arn:aws:iam::997532394226:user/jorgemf", return "997532394226"
        arn = self.RequireArn()
        return arn.split(':')[4]


    def GetTags(self):
        '''👉️ Returns the user tags.'''
        
        tags = self.GetStruct('Tags')
        
        # Tags won't be there if none are set.
        if not tags:
            return {}
        
        # Convert the tags to a dictionary.
        LOG.Print('🏷️ IAM_USER.GetTags:', tags)
        tagDict = {}
        for tag in STRUCT(tags).GetList():
            key = tag['Key']
            value = tag['Value']
            tagDict[key] = value

        return STRUCT(tagDict)
        
    
    def GetTag(self, name:str):
        '''👉️ Returns the value of a tag in the logged user.'''
        return self.GetTags().GetStr(name)
        