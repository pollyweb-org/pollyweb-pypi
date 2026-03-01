from pollyweb.utils.LOG import LOG
from LAMBDA_BASE import LAMBDA_BASE
from pollyweb.utils.STRUCT import STRUCT
import json


class LAMBDA_MOCK(LAMBDA_BASE):

    ICON= '🦙'
    

    _functions:dict[str,dict[str,object]] = {}
    _activeDomain:str = None
    


    @staticmethod
    def HelloWorld(event:any=None):
        return 'Hello World!'
    

    @classmethod
    def MockInvoke(cls, 
        alias:str, 
        handler:object=HelloWorld, 
        domain:str=None
    ):
        ''' 👉 Registers a fake lambda invocation handler.'''

        LOG.Print(cls.MockInvoke, f'{alias=}')

        if domain == None:
            domain = LAMBDA_MOCK._activeDomain

        if domain == None:
            LOG.RaiseValidationException('No domain set')

        if domain not in LAMBDA_MOCK._functions:
            LAMBDA_MOCK._functions[domain] = {}

        functions = LAMBDA_MOCK._functions[domain]
        functions[alias] = handler

    
    @classmethod
    def ResetMock(cls):
        ''' 👉 Resets the fake funcion dictionary.'''
        LAMBDA_MOCK._functions = {}


    @classmethod
    def SetMockDomain(cls, domain:str):
        LAMBDA_MOCK._activeDomain = domain