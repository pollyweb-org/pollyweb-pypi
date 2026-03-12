# 📚 HOST_APPENDIX

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations
from NLEEBB importNLWEBEB
from pollyweb import LOG
from pollyweb import STRUCT
from pollyweb import UTILS


class TALK_APPENDIX(STRUCT):
    ''' 
    {
        Locator     : 'https://...'
    }
    '''
    

    def RequireLocator(self, msg:str=None) -> str:
        return self.RequireStr('Locator')


    @staticmethod
    def New(type:str, locator:str):
        '''👉️ Inserts an appendix.
        * type: one of [ASSET,FILE,URL] constants.
        * locator: mapping of the appendix.'''

        # Validations will be done below.
        merge = TALK_APPENDIX({
            "Type": type,
            "Locator": locator
        })
        merge.VerifyAppendix()

        return merge


    def VerifyAppendix(self):
        self.RequireLocator()


    def ToInterface(self):
        if self.IsMissingOrEmpty():
            return None
        
        # Get the appendix type and locator.
        locator = self.RequireLocator()

        # Return Files.
        file = NLEEBB.ROLES().HOST().FILES().RequireFile(locator)

        ret = {
            "Name": file.RequireName()
        }

        serialized = file.GetSerialized()
        if not UTILS.IsNoneOrEmpty(serialized):
            ret["Serialized"] = file.GetSerialized()

        url = file.GetURL()
        if not UTILS.IsNoneOrEmpty(url):
            ret["URL"] = file.GetURL()

        return PROMPT_APPENDIX(ret)