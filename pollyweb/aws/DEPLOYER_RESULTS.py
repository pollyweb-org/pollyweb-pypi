from LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_RESULTS(STRUCT):
    

    def Require(self):
        if self.IsMissingOrEmpty():
            LOG.RaiseException(
                'No results set, call only OnExecute! ',
                'Are you wrongly running OnValidate?')
        return self
    

    def RequireDependency(self, key:str, type:type) -> str:
        '''👉️ Returns the dependency for the asset.'''
        return self.Require().GetDependency(key=key, type=type, require=True)


    def GetDependency(self, key:str, type:type, require:bool=False) -> str:   
        '''👉️ Returns the dependency for the asset.'''

        # Get the dependency.
        ret = self.Require().GetAtt(key, require=require)
        
        # Ensure the type.
        UTILS.AssertIsType(given=ret, expect=type, require=require)
        
        # Return the dependency.
        return ret
    

    def GetDependencyByType(self, type:type):   
        '''👉️ Returns the dependency for the asset.'''
        
        self.Require()

        # Get the dependency.
        for key, value in self.items():
            # Ensure the type.
            if isinstance(value, type):
                return value
        
        # Return the dependency.
        return None
    

    def RequireDependencyByType(self, type:type):   
        '''👉️ Returns the dependency for the asset.'''
        # Get the dependency.
        ret = self.Require().GetDependencyByType(type=type)
        # Ensure the dependency.
        UTILS.Require(ret)
        # Return the dependency.
        return ret