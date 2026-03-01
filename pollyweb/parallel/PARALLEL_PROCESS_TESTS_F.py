

from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import PW_UTILS as pw


class PARALLEL_PROCESS_TESTS_F(PARALLEL_TEST):

    ICON = '🧪'


    def _TestDirStructureHelper(self):
        

        pw.LOG.Print('Just testing a process...')
        
        return 123


    def TestDirStructure(self):
        pw.LOG.Print(self.TestDirStructure)
        
        name = 'box'
        
        pool = PARALLEL.PROCESS_POOL(
            name= name)

        ret = pool.RunProcess(
            handler= self._TestDirStructureHelper)
        
        pw.TESTS.AssertEqual(ret, 123)
        pw.TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        
        pw.LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestDirStructure()

        pw.LOG.PARALLEL().SetClassDone()