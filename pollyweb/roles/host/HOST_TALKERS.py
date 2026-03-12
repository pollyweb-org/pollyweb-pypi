# 📚 HOST_TALKER

from __future__ import annotations
from HOST_TALKER import HOST_TALKER

from PW_AWS.ITEM import ITEM
from PW_AWS.AWS import AWS
from pollyweb import UTILS


class HOST_TALKERS():
    ''' 🪣 List of talkers to be used by host locators.'''

    
    @staticmethod
    def _table():
        return AWS.DYNAMO('TALKERS')
    

    @classmethod
    def RequireTalker(cls, id:str) -> HOST_TALKER:
        '''👉 Gets the talker from the database.'''
        UTILS.AssertIsType(id, str)
        item = cls._table().Require(id)
        return HOST_TALKER(item)