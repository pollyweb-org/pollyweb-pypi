
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
import pollyweb.utils as pw


class PARALLEL_PROCESS_TESTS_I(PARALLEL_TEST):

    ICON = '🧪'


    def Helper(self):
        pw.LOG.Print(self.Helper, 
            f': Inside the thread helper.')
        # It has to be validation exception for this test to work.
        pw.LOG.RaiseValidationException('@: Error in thread')
       
    
    def TestExceptionInThread(self):
        try:
            PARALLEL.THREAD_POOL().RunThread(
                self.Helper)
        except Exception as e:
            if 'Error in thread' not in str(e) \
            or type(e) != pw.ValidationException:
                raise

        dir = pw.LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🔴 PARALLEL_PROCESS_TESTS_I.',
            fileNames= [
                'TestExceptionInThread.Helper',
                'TestExceptionInThread'
            ])


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        pw.LOG.Print(cls.TestAll)
        
        cls().TestExceptionInThread()

        pw.LOG.PARALLEL().SetClassDone()