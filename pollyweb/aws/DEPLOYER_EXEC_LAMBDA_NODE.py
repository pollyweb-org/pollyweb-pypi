from DEPLOYER_EXEC_LAMBDA import DEPLOYER_EXEC_LAMBDA
from aws.AWS import AWS
from aws.LAMBDA_FUNCTION_DEPLOY import LAMBDA_FUNCTION_DEPLOY
from LOG import LOG


class DEPLOYER_EXEC_LAMBDA_NODE(DEPLOYER_EXEC_LAMBDA):

    
    def OnValidate(self):
        '''👉️ Executes a Node task.'''
        LOG.Print('🏗️ DEPLOYER.EXEC.NODE.OnValidate()')

        super().OnValidate()

        self.VerifyAlienParameters([
            'Tests',
            'Environment',
            'Alias',
        ])
        
        # Zip the code.
        name = 'node/' + self.task.RequireName()
        dir = self.task.GetDirectory().GetSubDir(name).AssertExists()
        self.lambdaZip = dir.Zip()
        LAMBDA_FUNCTION_DEPLOY().ValidateZipBytes(self.lambdaZip)

        
    def OnExecute(self):
        #self.PostExecute()
        #return {}
        
        fn = AWS.LAMBDA(
            name= self.lambdaName,
            alias= self.lambdaAlias)
        
        tags = self.GetTags()

        fn.EnsureNodeLambda(
            zip= self.lambdaZip,
            tags= tags, 
            env= {})

        # Lambda dependencies grant invoke permission on them.

        self.PostExecute()

        return {
            'Arn': fn.GetArn(),
            'Name': fn.RequireName()
        }
