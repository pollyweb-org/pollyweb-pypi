from __future__ import annotations

from PW_UTILS.PYTHON_METHOD import PYTHON_METHOD
from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM_TYPE
from LOG import LOG

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

from PW_UTILS.TESTS import TESTS



class AWS_RESOURCE_WRAP:

    def __init__(self, 
        pool: AWS_RESOURCE_POOL[AWS_RESOURCE_ITEM_TYPE],
        name: str,
        client= None,
        resource= None,
        **args: dict,             
    ):
        self.pool = pool
        self.name = name
        self.client = client
        self.resource = resource
        self.args = args


    def __enter__(self):

        # Look for the resource with the given name.
        res = self.pool.Get(
            name= self.name, 
            client= self.client,
            resource= self.resource)
        
        # Delete if it exists.
        if res:
            res.Delete()
            res.AssertNotListed()

        # Get the Ensure() method.
        from PW_UTILS.PYTHON_METHOD import PYTHON_METHOD
        ensure = PYTHON_METHOD(self.pool._Ensure)

        # Create a payload with the args, the name, and client.
        ensureArgs= {}
        ensureArgs.update(dict(
            name= self.name,
            client= self.client))
        ensureArgs.update(self.args)

        # Invoke with the payload, leaving client as optional.
        res:AWS_RESOURCE_ITEM_TYPE = ensure.InvokeWithMatchingArgs(
            args= ensureArgs,
            optional= ['client'])
        
        # Invoking again shouldn't fail.
        ensure.InvokeWithMatchingArgs(
            args= ensureArgs,
            optional= ['client'])
        
        # Verify the resource exists.
        res.AssertExists()
    
        # Update.
        self.pool.Update(
            res= res, 
            args= self.args)

        # Require.
        res2 = self.pool.Require(
            name= self.name, 
            client= self.client,
            resource= self.resource)
        TESTS.AssertEqual(res2.Arn, res.Arn)

        self.res = res

        return res


    def __exit__(self, exc_type, exc_val, exc_tb):

        # Cleanup.
        self.res.Delete()
        self.res.AssertNotListed()
        
        return True
    


class AWS_RESOURCE_POOL(ABC, Generic[AWS_RESOURCE_ITEM_TYPE]):
    '''👉️ Manages a pool of AWS resources.
    
    Implement the following methods:
      * Create(name:str, args:dict, client) -> AWS_RESOURCE_ITEM_TYPE
      * Ensure(name:str) -> AWS_RESOURCE_ITEM_TYPE
      * List(client=None) -> list[AWS_RESOURCE_ITEM_TYPE]
      * Update(res:AWS_RESOURCE_ITEM_TYPE, args:dict)
    ):
    '''

    
    @classmethod
    @abstractmethod
    def Ensure(cls, 
        name:str
    ):
        '''👉️ Ensures a resource exists.
         * If it does not exist, it is created.
         * If it does exist, returns the resource.
        '''
        raise Exception('Implement') 
      

    @classmethod
    @abstractmethod
    def List(cls, 
        client= None,
        resource= None
    ) -> list[AWS_RESOURCE_ITEM_TYPE]:
        '''👉️ Returns a list of all resources.'''
        raise Exception('Implement')


    @classmethod
    def _List(cls, 
        client= None,
        resource= None
    ) -> list[AWS_RESOURCE_ITEM_TYPE]:
        '''👉️ Returns a list of all resources.'''
        
        LOG.Print(f'@')
        
        # make the client argument optional.
        method = PYTHON_METHOD(cls.List)
        return method.InvokeWithMatchingArgs(
            args= dict(
                client= client,
                resource= resource),
            optional= [
                'client', 
                'resource'])


    @classmethod
    @abstractmethod
    def Create(cls, 
        name: str,
        client= None,
        resource= None,
        **args: dict
    ) -> AWS_RESOURCE_ITEM_TYPE:
        '''👉️ Creates a new resource.'''
        raise Exception('Implement')
    

    @classmethod
    def Update(cls, 
        res: AWS_RESOURCE_ITEM_TYPE,
        **args: dict
    ):
        '''👉️ Updates an existing resource.'''
        pass


    @classmethod
    def Get(cls, 
        name:str,
        client= None,
        resource= None
    ) -> AWS_RESOURCE_ITEM_TYPE:
        '''👉️ Returns a resource by name.'''

        LOG.Print(f'@: {name=}')

        items = cls._List(
            client= client,
            resource= resource)
        
        LOG.Print(f'@: {len(items)=}')
        for res in items:
            if res.Name == name:
                return res
            
        return None
    

    @classmethod
    def Require(cls, 
        name:str,
        client= None,
        resource= None
    ) -> AWS_RESOURCE_ITEM_TYPE:
        '''👉️ Requires a resource exists.
         * `name`: The name of the resource.
         * `client`: The boto3 client for API calls.
         * `resource`: The boto3 resource for API calls.
        '''

        LOG.Print(f'@: {name=}')

        res = cls.Get(
            name= name, 
            client= client,
            resource= resource)
        
        if not res:
            LOG.RaiseValidationException(
                f'{name} not found')

        return res
    

    @classmethod
    def _Ensure(cls, 
        name: str,
        client:any= None,
        resource:any= None,
        rebuild:bool= False,
        **kwargs
    ) -> AWS_RESOURCE_ITEM_TYPE:
        '''👉️ Ensures a resource exists.
            * If it does not exist, it is created.
            * If it does exist, it is updated.
            * Returns the resource.
        '''

        LOG.Print(f'@: {name=}')

        # Look for existing.
        res = cls.Get(
            name= name, 
            client= client,
            resource= resource)
        
        if res:
            if rebuild:
                res.Delete()    
                LOG.Print('@: Deleted to rebuild', res)
            else:
                cls.Update(
                    res=res, 
                    args=kwargs)     
                           
                LOG.Print('@: Updated', res)
                return res
        
        # Create if not exists.
        res:AWS_RESOURCE_ITEM_TYPE 
        createMethod = PYTHON_METHOD(cls.Create)

        res= createMethod.InvokeWithMatchingArgs(
            args= dict(
                name= name, 
                client= client, 
                resource= resource, 
                **kwargs),
            optional= [
                'client',
                'resource'
            ])
        
        # Wait until is listed.
        res.WaitUntilListed()
        
        LOG.Print('@: Created', res)
        return res
    

    @classmethod
    def Exists(cls, 
        name:str, 
        client=None,
        resource=None
    ):
        '''👉️ Returns True if the resource exists.'''

        res = cls.Get(
            name= name, 
            client= client,
            resource= resource)
        
        return res != None
    

    @classmethod
    def Test(cls, 
        name:str, 
        client=None,
        resource=None,
        **args
    ) -> AWS_RESOURCE_ITEM_TYPE:
        '''👉️ Wraps a resource.'''
        
        return AWS_RESOURCE_WRAP(
            pool= cls,
            name= name,
            client= client,
            resource= resource,
            **args)
