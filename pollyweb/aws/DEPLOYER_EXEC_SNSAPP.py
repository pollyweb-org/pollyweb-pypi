from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from pollyweb.utils.UTILS import UTILS
from aws.AWS import AWS 

class DEPLOYER_EXEC_SNSAPP(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):
        
        self.VerifyAlienParameters([
            'FirebaseKey'
        ])

        dir = self.task.GetDirectory()
        firebaseKeyPath = self.task.GetStringParam('FirebaseKey')
        file = dir.GetFile(firebaseKeyPath)
        file.AssertExists()
        self.firebaseKey = file.ReadText()

        self.appName = self.task.RequireFullName()
    

    def OnExecute(self):
        
        AWS.SNS().RegisterFirebase(
            name= self.appName,
            serverKey= self.firebaseKey)
        