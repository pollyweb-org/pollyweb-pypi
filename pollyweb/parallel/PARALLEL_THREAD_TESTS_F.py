

from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_THREAD_TESTS_F(PARALLEL_TEST):

    ICON = '🧪'


    def _TestDuplicateNamesHelper(self):
        return 1


    def TestDuplicateNames(self):
        
        # OK to add an anonymous pool per method.
        PARALLEL.THREAD_POOL()
        
        # Don't add another anonymous pool in the same method.
        #with pw.TESTS.AssertValidation():  # This is not working, maybe because of __exit__
        try:
            PARALLEL.THREAD_POOL()
        except AssertException:
            pass
        
        # Add a name to avoid the error.
        PARALLEL.THREAD_POOL(name='Pool1')
        
        # Don't duplicate the name.
        #with pw.TESTS.AssertValidation(): # This is not working, maybe because of __exit__.
        try:
            PARALLEL.THREAD_POOL(name='Pool1')
        except pw.AssertException:
            pass

        # Add a different name to avoid the error.
        PARALLEL.THREAD_POOL(name='Pool2')

        pw.LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestDuplicateNames()
        
        pw.LOG.PARALLEL().SetClassDone()