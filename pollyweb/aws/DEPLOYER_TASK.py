from aws.ITEM import ITEM
from LOG import LOG
from PW_UTILS.STRUCT import STRUCT   
from PW_UTILS.UTILS import UTILS 

class DEPLOYER_TASK(ITEM):
    '''
    Example:
        Stack: <SyncApi>
        Asset: CloudFront
        Type: CloudFront
        Params: 
            <name>: <value>
            <name>: <value>
        StackParams:
            <name>: <value>
            <name>: <value>
        Dependencies:
            - GlobalCertificate
            - GlobalWebAcl
            - RestApi
            - DomainName
        Status: PENDING
        Result: <any>
    '''

    ICON = '🏗️'
    

    @staticmethod
    def New( 
        path:str,
        stack:str, 
        asset:str, 
        type:str, 
        params:STRUCT|dict, 
        stackParams:STRUCT|dict,
        dependencies:list[str] = None
    ):
        '''👉️ Creates a new DEPLOYER_TASK.'''

        # Ensure the parameters.        
        UTILS.AssertStrings([stack, asset, type], require=True   )
        STRUCT.AssertClass(params, require=True)
        STRUCT.AssertClass(stackParams, require=True)
        UTILS.AssertIsList(dependencies, itemType=str)

        # Initialize the base class.
        ret = DEPLOYER_TASK({
            'Path': path,
            'Stack': stack,
            'Asset': asset,
            'Type': type,
            'Params': UTILS.Default(params, {}),
            'StackParams': UTILS.Default(stackParams, {}),
            'Dependencies': dependencies or [],
            'Status': 'PENDING',
            'Result': None
        })
        ret.Verify()

        return ret


    def RequireFullName(self) -> str:
        '''👉️ Returns the `{stack}-{name}` of the asset.'''
        return f'{self.RequireStackName()}-{self.RequireAsset()}'
    

    def RequireTypeAndFullName(self) -> str:
        '''👉️ Returns the type and full name of the asset.'''
        return f'{self.RequireType()}|{self.RequireFullName()}'


    def RequireStackName(self):
        '''👉️ Returns the stack name.'''
        stack = self.RequireStr('Stack')
        return stack
    

    def RequireFileName(self) -> str:
        '''👉️ Returns the file name of the asset.'''
        return f'🧱 {self.RequireStackName()}.yaml'
    
    
    def Exception(self, msg:str):
        '''👉️ Logs an exception.'''
        LOG.RaiseException(
            msg, 
            f'file: {self.RequireFileName()}', 
            f'name: {self.RequireFullName()}', 
            self)
        

    def RequireName(self) -> str:
        '''👉️ Returns the asset name.'''
        return self.RequireStr('Asset')


    def RequireAsset(self) -> str:
        '''👉️ Returns the asset name.'''
        return self.RequireStr('Asset')
    

    def RequireType(self) -> str:   
        '''👉️ Returns the type of the asset.'''
        return self.RequireStr('Type')  
    

    def HasDependencies(self) -> bool:
        '''👉️ Returns True if the asset has dependencies.'''
        return len(self.GetDependencies()) > 0


    def GetDependencies(self) -> list[str]:
        '''👉️ Returns the dependencies for the asset.'''
        return self.ListStr('Dependencies')
    
    
    def RequireDependencies(self) -> list[str]:   
        '''👉️ Returns the dependencies for the asset.'''
        ret = self.ListStr('Dependencies', require=True)
        return ret

    
    def RequireParams(self) -> STRUCT:
        '''👉️ Returns the params for the asset.'''
        self.Require()
        ret = self.GetStruct('Params', default=STRUCT({}))
        return ret
        

    def GetParam(self, key:str):
        '''👉️ Returns the param for the asset.'''
        LOG.Print(f'@({key})', f'{key=}', self)
        self.Require()
        params = self.RequireParams()
        return params.GetAtt(key)
    

    def RequireDictParam(self, key:str):
        '''👉️ Returns the param for the asset.'''
        return self.Require().RequireParams().RequireDict(key)
    

    def RequireStringParam(self, key:str):
        '''👉️ Returns the param for the asset.'''
        return self.Require().RequireParams().RequireStr(key)


    def GetStringParam(self, key:str, default:str=None):
        '''👉️ Returns the param for the asset.'''
        ret = self.GetParam(key)
        UTILS.AssertIsStr(ret)
        if ret == None and default != None:
            return default
        return ret
    

    def GetBoolParam(self, key:str, default:bool=False):
        '''👉️ Returns the param for the asset.'''
        ret = self.GetParam(key)
        UTILS.AssertIsBool(ret)
        if ret == None and default != None:
            return default
        return ret
    

    def GetIntParam(self, key:str, default:int=0):
        '''👉️ Returns the param for the asset.'''
        ret = self.GetParam(key)
        UTILS.AssertIsInt(ret)
        if ret == None and default != None:
            return default
        return ret


    def GetListParam(self, key:str, itemType:type, default:list=[]):
        '''👉️ Returns the param for the asset.'''
        ret = self.GetParam(key)
        UTILS.AssertIsList(ret, itemType=itemType)
        if ret == None and default != None:
            return default
        return ret
    

    def GetDictParam(self, key:str, itemType:type, default:dict={}):
        '''👉️ Returns the param for the asset.'''
        ret = self.GetParam(key)
        UTILS.AssertIsDict(ret, itemType=itemType)
        if ret == None and default != None:
            return default
        return ret
    

    def RequireParam(self, key:str):
        '''👉️ Returns the param for the asset.'''
        return self.Require().RequireParams().RequireAtt(key)


    def RequireStackParams(self) -> STRUCT:
        '''👉️ Returns the stack params for the asset.'''
        ret = self.GetStruct('StackParams', default=STRUCT({}))
        return ret
    

    def GetStackParam(self, key:str):
        '''👉️ Returns the stack param for the asset.'''
        return self.Require().RequireStackParams().GetAtt(key)
    

    def RequireStackParam(self, key:str):
        '''👉️ Returns the stack param for the asset.'''
        return self.Require().RequireStackParams().RequireAtt(key)


    def RequireStatus(self) -> str:
        '''👉️ Returns the status of the asset.'''
        return self.Require().RequireStr('Status')
    

    def IsPending(self) -> bool:
        '''👉️ Returns True if the asset is pending.'''
        return self.Require().RequireStatus() == 'PENDING'
    

    def MarkAsFinished(self, result:any):
        '''👉️ Marks the task as finished.'''
        self.SetAtt('Status', 'FINISHED')
        self.SetAtt('Result', result)


    def GetResult(self):
        '''👉️ Returns the result of the asset.'''
        return self.GetAtt('Result')


    def RequireResult(self):
        '''👉️ Returns the result of the asset.'''
        val = self.GetResult()
        UTILS.Require(val, 
            msg=f'Result not set for task: {self.RequireFullName()}')
        return val
    

    def RequireResultStruct(self):
        '''👉️ Returns the result of the asset.'''
        return STRUCT(self.RequireResult())
    

    def EnsureIsPending(self):
        '''👉️ Ensures the asset is pending.'''
        if not self.IsPending():
            raise ValueError(f'Task is not pending: {self}')
        

    def EnsureIsFinished(self):
        '''👉️ Ensures the asset is finished.'''
        if self.IsPending():
            raise ValueError(f'Task is not finished: {self}')
        

    def RequirePath(self) -> str:
        '''👉️ Returns the path of the asset.'''
        return self.RequireStr('Path')
    

    def GetDirectory(self):
        '''👉️ Returns the directory of the asset.'''
        stackPath = self.RequirePath()
        directory = UTILS.File(stackPath).GetParentDir()
        directory.AssertExists()
        return directory


    def Verify(self):
        '''👉️ Verifies the object.'''
        self.RequirePath()
        self.RequireStackName()
        self.RequireAsset()
        self.RequireType()
        self.RequireParams()
        self.RequireStackParams()
        self.RequireDependencies()
        self.RequireStatus()
        self.GetResult()
        self.GetDirectory()
        return self