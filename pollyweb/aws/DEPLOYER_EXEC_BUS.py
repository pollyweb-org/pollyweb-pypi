from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK

class DEPLOYER_EXEC_BUS(DEPLOYER_EXEC_TASK):
    pass


    def OnValidate(self):
        pass


    def OnExecute(self):
        return {}
    
        name = self.task.RequireFullName()
        from PW_AWS.EVENTBRIDGE_REAL_BUS import EVENTBRIDGE_REAL_BUS
        EVENTBRIDGE_REAL_BUS(name).EnsureExists()
        return {
            'Name': name
        }