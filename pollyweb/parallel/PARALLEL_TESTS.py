import PW_UTILS as pw


class PARALLEL_TESTS():

    ICON = '🧪'
    

    @classmethod
    def TestAllParallel(cls):
        pw.LOG.Print(cls.TestAllParallel)
        
        # Not used anymore.
        #PARALLEL_DISPLAY_TESTS.TestParallelDisplay()
        
        from .PARALLEL_LOG_TESTS import PARALLEL_LOG_TESTS
        PARALLEL_LOG_TESTS.TestParallelLog() #1 

        from .PARALLEL_THREAD_TESTS import PARALLEL_THREAD_TESTS
        PARALLEL_THREAD_TESTS.TestThreads() #2

        from .PARALLEL_PROCESS_TESTS import PARALLEL_PROCESS_TESTS
        PARALLEL_PROCESS_TESTS.TestAll() #3
        