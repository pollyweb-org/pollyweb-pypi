
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST


import PW_UTILS as pw


class PARALLEL_PROCESS_TESTS_E(PARALLEL_TEST):

    ICON = '🧪'


    def _TestLogErrorHelper1(self):
        pw.UTILS.Sleep(0.1)
        print(1/0)

    
    def _TestLogErrorHelper2(self):
        pw.UTILS.Sleep(0.1)
        print(1/0)

    
    def TestLogError(self):
        pw.LOG.Print(self.TestLogError)
         
        # Without join.
        with pw.TESTS.AssertValidation(check='division by zero'):
            with PARALLEL.PROCESS_POOL() as pool:
                pool.StartProcess(self._TestLogErrorHelper1)
                pool.StartProcess(self._TestLogErrorHelper2)

        # With join.
        with pw.TESTS.AssertValidation(check='division by zero'):
            with PARALLEL.PROCESS_POOL() as pool:
                pool.StartProcess(self._TestLogErrorHelper1).Join()
            
        pw.LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestLogError()

        pw.LOG.PARALLEL().SetClassDone()