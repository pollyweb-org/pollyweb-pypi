from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import PW_UTILS as pw


class PARALLEL_PROCESS_TESTS_H(PARALLEL_TEST):

    ICON = '🧪'


    def Handler(self):
        pw.LOG.Print(self.Handler, 
            f': Inside the process helper.')
        
        # Here, it can be any exception type, not just validation exception.
        pw.LOG.RaiseException('@: Error in process')
       
    
    def TestExceptionInProcess(self):
        try:
            PARALLEL.PROCESS_POOL().RunProcess(
                self.Handler)
        except Exception as e:
            if 'Error in process' not in str(e) \
            or type(e) != pw.ValidationException:
                raise

        dir = pw.LOG.PARALLEL().SetMethodDone()
        
        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🔴 PARALLEL_PROCESS_TESTS_H.',
            fileNames= [
                'TestExceptionInProcess.Handler',
                'TestExceptionInProcess'
            ])


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestExceptionInProcess()

        pw.LOG.PARALLEL().SetClassDone()