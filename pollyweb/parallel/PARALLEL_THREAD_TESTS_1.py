from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_THREAD_TESTS_1(PARALLEL_TEST):

    ICON = '🧪'


    def Handler(self, val:int):
        pw.LOG.Print('Inside Handler')
        self.total += val
        return 999
    

    def TestExecution(self):
        import shutil
        
        self.total = 0

        pool = PARALLEL.THREAD_POOL()

        # Without with: the threads are not automatically executed.
        pool.AddThread(
            handler= self.Handler, 
            args= dict(val= 123))
        pw.TESTS.AssertEqual(self.total, 0)

        # We need to run the threads manually.
        ret = pool.RunAllThreads()
        pw.TESTS.AssertEqual(self.total, 123)
        
        # Check if the return value is correct.
        pw.TESTS.AssertEqual(len(ret.Keys()), 1)
        pw.TESTS.AssertEqual(ret.RequireAtt('Handler'), 999)
        
        shutil.rmtree('__dumps__/PARALLEL/🟢 PARALLEL_THREAD_TESTS_1.TestExecution', ignore_errors=True)
        dir = pw.LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_THREAD_TESTS_1.',
            fileNames= [
                'TestExecution', # the pool
                'TestExecution.Handler' # the thread
            ],
            containsLines= [
                'Inside Handler'
            ])
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        pw.LOG.Print(cls.TestAll)

        cls().TestExecution()
        
        pw.LOG.PARALLEL().SetClassDone()