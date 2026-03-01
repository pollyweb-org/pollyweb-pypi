from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_RESULTS import DEPLOYER_RESULTS
from DEPLOYER_TASK import DEPLOYER_TASK

from dataclasses import dataclass, asdict, field

from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS

@dataclass
class DEPLOYER_EXEC_ARGS(PRINTABLE):
    '''👉️ Arguments for the deployer execution.'''

    deployArgs: DEPLOYER_ARGS
    '''👉️ Deployment options.'''
    
    task: DEPLOYER_TASK
    '''👉️ Task to execute.'''

    taskDict: dict[str, DEPLOYER_TASK]
    '''👉️ Dictionary of tasks.'''

    layerArns: list[str]= field(default_factory=list)
    '''👉️ Layer ARNs.'''

    results: DEPLOYER_RESULTS= field(default_factory=DEPLOYER_RESULTS)
    '''👉️ Results of the execution.'''

    simulate: bool = True
    '''👉️ Simulation mode.'''


    def __post_init__(self):
        # Ensure the parameters.
        UTILS.AssertIsType(self.deployArgs, DEPLOYER_ARGS, require=True)
        UTILS.AssertIsType(self.task, DEPLOYER_TASK, require=True)
        UTILS.AssertIsType(self.results, DEPLOYER_RESULTS)

        # 👉️ Prepare the log
        PRINTABLE.__init__(self, dict(
            simulate= self.simulate,
            deployArgs= self.deployArgs,
            task= self.task,
            layerArns= len(self.layerArns),
            taskDict= STRUCT(self.taskDict).Length(),
            results= self.results
        ))