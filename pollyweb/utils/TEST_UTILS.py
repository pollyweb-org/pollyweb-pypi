class TEST_UTILS:


    @classmethod
    def Run(cls):

        # -----------------------------
        # Log.
        # -----------------------------

        from .STDOUT_TEST import STDOUT_TEST
        STDOUT_TEST.TestAllStdOut()

        from .LOG_TESTS import LOG_TESTS
        LOG_TESTS.TestAllLogs()

        # -----------------------------
        # Utils.
        # -----------------------------
        
        from .TESTS_TESTS import TESTS_TESTS
        TESTS_TESTS.TestAllTests()
        
        from .UTILS_TESTS import UTILS_TESTS
        UTILS_TESTS.TestAllUtils()
                
        from .STRUCT_TESTS import STRUCT_TESTS
        STRUCT_TESTS.TestAllStruct()

        from .FILESYSTEM_TESTS import FILESYSTEM_TESTS
        FILESYSTEM_TESTS.TestAllFileSystem()

        from .FILE_TESTS import FILE_TESTS
        FILE_TESTS.TestAllFile()

        from .DIRECTORY_TESTS import DIRECTORY_TESTS
        DIRECTORY_TESTS.TestAllDirectory()
 
        # -----------------------------
        # Log Buffer
        # -----------------------------

        from .LOG_BUFFER_TEST import LOG_BUFFER_TEST
        LOG_BUFFER_TEST.TestAllLogBuffer()

        # -----------------------------
        # PARALLEL 
        # -----------------------------

        #TODO: move to another project.
        #from PARALLEL_TESTS import PARALLEL_TESTS
        #PARALLEL_TESTS.TestAllParallel()


    @classmethod
    def TestUtils(cls):

        from .LOG import LOG
        
        cls.Run()
