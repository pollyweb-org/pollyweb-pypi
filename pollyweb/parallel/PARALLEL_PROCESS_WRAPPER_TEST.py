
from .PARALLEL_PROCESS_WRAPPER import PARALLEL_PROCESS_WRAPPER

import pollyweb.utils as pw

class PARALLEL_PROCESS_WRAPPER_TEST:


    @classmethod
    def TestMethod(cls, fruit:str):
        return f'Yes, {fruit} is nice.'


    @classmethod
    def OnDone(cls, name:str):
        pw.LOG.Print(f'Process {name} done.')

    @classmethod    
    def TestAll(cls):
        
        PARALLEL_PROCESS_WRAPPER.Wrap(
            name= 'TestWrapper',
            handler= cls.TestMethod,
            args= {'fruit': 'pineapple'},
            share= {},
            logPath= 'parallel-process-wrapper-test.md',
            writeToConsole= True,
            testFast= False,
            onDone= cls.OnDone
        )
        
        pw.LOG.Print('PARALLEL_PROCESS_WRAPPER_TEST completed.')