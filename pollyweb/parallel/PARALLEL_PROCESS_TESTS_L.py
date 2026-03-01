
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_PROCESS_TESTS_L(PARALLEL_TEST):

    ICON = '🧪'
    

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        pw.LOG.Print(cls.TestAll)
        
        #cls().TestProcessPool()

        pw.LOG.PARALLEL().SetClassDone()