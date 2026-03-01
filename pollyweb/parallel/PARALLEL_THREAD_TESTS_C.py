

from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_THREAD_TESTS_C(PARALLEL_TEST):

    ICON = '🧪'


    def Helper(self):
        return 1/0


    def TestFailureRunTaskList(self):

        # Expect a division by zero error.
        with pw.TESTS.AssertValidation(type= ZeroDivisionError):
            pool = PARALLEL.THREAD_POOL()
            pool.RunThreadList([
                self.Helper
            ])

        # Verify the status.
        pw.TESTS.AssertEqual(pool.GetLog().GetStatus(), 'FAILED')
        pw.TESTS.AssertEqual(pool.GetLog().GetIconName(), 'FAILED')
        pw.TESTS.AssertEqual(pool.GetLog().GetNameWithoutIcon(), 
            f'{PARALLEL_THREAD_TESTS_C.__name__}.'
            f'{PARALLEL_THREAD_TESTS_C.TestFailureRunTaskList.__name__}.md')
        
        dir = pw.LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🔴 PARALLEL_THREAD_TESTS_C.',
            fileNames= [
                'TestFailureRunTaskList',
                'TestFailureRunTaskList.Helper'
            ],
            containsText= [
                'ZeroDivisionError'
            ])


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestFailureRunTaskList()
        
        pw.LOG.PARALLEL().SetClassDone()
