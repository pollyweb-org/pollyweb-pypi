# 📚 DYNAMO

import boto3

from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from pollyweb.utils.STRUCT import STRUCT
dynamoResource = boto3.resource('dynamodb')

import os

from DYNAMO_REAL_TABLE_STRUCT import DYNAMO_REAL_TABLE_STRUCT
from DYNAMO_BASE import DYNAMO_BASE, DYNAMO_BASE_TABLE
from pollyweb.utils.UTILS import UTILS
from pollyweb.utils.LOG import LOG


class DYNAMO_REAL(DYNAMO_BASE):
    '''👉 Real implementation of Dynamo.'''


    def __init__(self, 
        alias: str=None, 
        keys: list[str]=None,
        name: str=None,
    ) -> None:
        super().__init__(alias=alias, keys=keys)
        self._table = None
        self._name = name
    

    @classmethod
    def BACKUP(cls): 
        from DYNAMO_BACKUP import DYNAMO_BACKUP
        return DYNAMO_BACKUP()
    

    @classmethod
    def CLIENT(cls):
        from DYNAMO_REAL_CLIENT import DYNAMO_REAL_CLIENT
        return DYNAMO_REAL_CLIENT()    


    def Table(self):
        '''👉 Returns the underlying table.'''

        # Check the cache.
        if self._table:
            return self._table
        
        # Require an alias.
        if not self._name:
            
            if not self._alias:
                LOG.RaiseException('Set the alias to use a table!')

            lookup = f'Dynamo_{self._alias}_Name'
            if lookup in os.environ:
                self._name = os.environ[lookup]
            elif self._alias in os.environ:
                self._name = os.environ[self._alias]
            else:
                LOG.RaiseException(
                    f'Table alias not found in the os environment: {self._alias}!', 
                    self)
                
        
        # Get the table from AWS.
        realTable= dynamoResource.Table(self._name)
        wrapTable = DYNAMO_REAL_TABLE_STRUCT(
            alias= self._alias,
            name= self._name, 
            table= realTable)

        # Add to cache an return.
        self._table = wrapTable
        return self._table


    def TriggerLambda(self, fn: LAMBDA_FUNCTION_REAL) -> None:
        '''👉️ Triggers a lambda on a DynamoDB stream.'''
        LOG.Print(f'@: {fn.RequireName()}')
        self.Table().TriggerLambda(fn)