
from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from LOG import LOG
from pollyweb.utils.UTILS import UTILS


class DEPLOYER_EXEC_DUMMY(DEPLOYER_EXEC_TASK):


    def OnVerify(self):
        pass


    DummyExecutions = []
    '''👉️ A list of executed Dummy tasks.'''


    def OnExecute(self):
        name = self.task.RequireFullName()
        lst = DEPLOYER_EXEC_DUMMY.DummyExecutions
        allTasks = self.taskDict

        if UTILS.Length(allTasks) == 0:
            LOG.RaiseException('Task dictionary is empty!')

        # Raise an exception if there are tasks in the list that don't belong to the task dictionary. 
        for taskName in lst:
            from pollyweb.utils.STRUCT import STRUCT
            keys = STRUCT(allTasks).Keys()
            if taskName not in keys:
                LOG.RaiseException(
                    'Task not found in task dictionary!', 
                    f'task={taskName}',
                    f'list={lst}', 
                    f'keys={keys}')

        # Raise an exception if the task is already added.
        if name in lst:
            LOG.RaiseException(
                'Task already executed!', 
                f'task={name}',
                f'list={lst}', lst)

        # Append the task to the list.
        lst.append(name)
        
        # Return the result.
        return {
            'Executed': self.task.RequireFullName()
        }
    