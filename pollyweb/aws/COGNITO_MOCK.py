from __future__ import annotations

from pollyweb.utils.LOG import LOG


class COGNITO_MOCK:
    
    @classmethod
    def CreateUser(cls, username, password, clientAlias='COGNITO'): 
        pass