from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
import pollyweb.utils as pw


class PARALLEL_THREAD_TESTS_2(PARALLEL_TEST):

    ICON = '🧪'


    def Handler(self, val:int):
        self.total += val


    def TestExecution(self):
        
        self.total = 0

        # With with: the threads are automatically executed.
        with PARALLEL.THREAD_POOL() as pool:
            pool.AddThread(
                handler= self.Handler,
                args= dict(val= 123))
        
        pw.TESTS.AssertEqual(self.total, 123)
        
        dir = pw.LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_THREAD_TESTS_2.',
            fileNames= [
                'TestExecution', # the pool
                'TestExecution.Handler' # the thread
            ])
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        pw.LOG.Print(cls.TestAll)

        cls().TestExecution()
        
        pw.LOG.PARALLEL().SetClassDone()