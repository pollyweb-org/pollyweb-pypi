# 📚 HOST_ASSET

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.ITEM import ITEM
from PW_AWS.AWS import AWS


class HOST_ASSET(ITEM):
    ''' 🪣 
    {
        ID: menu-drinks-en
        Name: menu-drinks.jpeg
        URL: 'https://...'
    }
    '''

    
    @staticmethod
    def _table():
        return AWS.DYNAMO('ASSETS')
    

    @staticmethod
    def RequireAsset(assetID:str) -> HOST_ASSET:
        item = HOST_ASSET._table().Require(assetID)
        ret = HOST_ASSET(item)
        return ret
    
    
    def RequireURL(self, msg:str=None) -> str:
        '''👉 The external location of the asset.'''
        return self.RequireStr('URL', msg=msg)  

