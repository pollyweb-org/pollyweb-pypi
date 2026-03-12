# 📚 HOST_LOCATOR

from __future__ import annotations

from PW_AWS.ITEM import ITEM
from PW_AWS.AWS import AWS
from EPHEMERAL_HOST_LOCATOR import EPHEMERAL_HOST_LOCATOR


class HOST_LOCATOR(EPHEMERAL_HOST_LOCATOR, ITEM):
    ''' 🪣 Holds all the place locators for the host.
    {
        ID: pollyweb.org/HOST,SALON
        Talker: DefaultTalker
        Ephemeral: 
            Device: 01f08ea1-2b6b-4796-b95d-e6d0656bf31c
            Supplier: ephemeral.any-supplier.org
            Pin: 7263   
            Expires: '2023-09-23T12:45:23.000Z'
    }
    '''

    
    @staticmethod
    def _table():
        return AWS.DYNAMO('LOCATORS')
    

    @classmethod
    def RequireLocator(cls, code:str, locator:str) -> HOST_LOCATOR:
        '''👉 Gets the locator from the database.'''
        id = f'{code},{locator}'
        item = cls._table().Require(id)
        return cls(item)


    def RequireTalker(self) -> str:
        '''👉 ID of the Talker.'''
        return self.RequireStr('Talker')
    
    