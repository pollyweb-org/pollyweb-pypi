class TEST_PARALLEL:


    @classmethod
    def Run(cls):

        # -----------------------------
        # PARALLEL 
        # -----------------------------

        from .PARALLEL_TESTS import PARALLEL_TESTS
        PARALLEL_TESTS.TestAllParallel()


    @classmethod
    def TestParallel(cls):

        
        cls.Run()

        #TODO: move to another project.
        #from PARALLEL import  PARALLEL
        #with PARALLEL.THREAD_POOL() as pool:
        #    pool.RunThread(cls.Run)
        #pw.LOG.PARALLEL().SetClassDone()
