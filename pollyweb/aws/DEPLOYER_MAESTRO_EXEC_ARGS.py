from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_TASK import DEPLOYER_TASK

from dataclasses import dataclass, asdict

from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.UTILS import UTILS

@dataclass
class DEPLOYER_MAESTRO_EXEC_ARGS(PRINTABLE):
    '''👉️ Defines the arguments for executing a list of tasks.'''

    Tasks: list[DEPLOYER_TASK]
    '''👉️ List of tasks to execute.'''

    AssertMethod:callable= None
    '''👉️ Method to assert the results.'''


    def __post_init__(self):
        
        # 👉️ Ensure the tasks are of the correct type
        UTILS.AssertIsList(self.Tasks, 
            itemType= DEPLOYER_TASK, 
            require= True)    
        
        # 👉️ Prepare the log
        PRINTABLE.__init__(self, dict(
            tasks= len(self.Tasks),
            assertMethod= self.AssertMethod
        ))