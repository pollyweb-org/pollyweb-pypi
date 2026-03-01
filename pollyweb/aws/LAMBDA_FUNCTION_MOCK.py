from LAMBDA_FUNCTION import LAMBDA_FUNCTION
from LAMBDA_MOCK import LAMBDA_MOCK
from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
import json


class LAMBDA_FUNCTION_MOCK(LAMBDA_FUNCTION):

    ICON= '🦙'
        

    def __init__(self, alias:str=None):
        self._alias = alias


    def Invoke(self, params:any={}) -> STRUCT:
        ''' 👉 Fakes a lambda invocation, by calling the python method directly.'''
        
        LOG.Print('🦙 LAMBDA.MOCK.Invoke()', params)

        if params == None:
            LOG.RaiseValidationException('Cannot invoke with None!')

        from NLWEB import NLWEB
        domain = NLWEB.CONFIG().RequireDomain()
        LOG.Print(
            f'🦙 LAMBDA.MOCK.Invoke()',
            f'Alias= {self._alias}',
            f'Domain= {domain}',
            f'Params=', params)

        if domain not in LAMBDA_MOCK._functions:
            LOG.RaiseValidationException(
                f'🦙 First, define the Lambda alias=({self._alias}) in domain=({domain})!')
            
        functions = LAMBDA_MOCK._functions[domain]
        if self._alias not in functions:
            LOG.RaiseValidationException(
                f'🦙 First, define the Lambda alias=({self._alias}) in domain=({domain})!')
        
        event = json.loads(json.dumps(params))
        function = functions[self._alias]
        result = function(event)

        LOG.Print(
            f'🦙 LAMBDA.MOCK.Invoke: returned!', 
            f'Domain= {domain}',
            f'Alias= {self._alias}',
            f'Function= {function.__name__}',
            f'Result.Type= {type(result).__name__}',
            f'Result=', result)
        
        return STRUCT(result)
