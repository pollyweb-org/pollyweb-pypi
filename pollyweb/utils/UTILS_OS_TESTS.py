from .LOG import LOG
from .TESTS import TESTS
from .UTILS import UTILS
from .TESTS import ValidationException


class UTILS_OS_TESTS:


    @classmethod
    def TestAllOS(cls):
        LOG.Print('@')

        cls.TestDirectory()
        cls.TestExecuteStringCommand()
        cls.TestExecuteRejectsShellMetacharacters()

        
    @classmethod
    def TestDirectory(cls):
        LOG.Print('@')
        
        dir = LOG.GetLogDir()
        dir.AssertExists()
        TESTS.AssertEqual(
            dir.GetName(), '__dumps__')
        
        dir = dir.GetSubDir('UTILS_OS_TESTS')
        TESTS.AssertEqual(
            dir.GetName(), 'UTILS_OS_TESTS')
        
        # Test the home directory.
        dir = UTILS.OS().Directory('~')
        TESTS.AssertTrue(
            dir.GetPath().startswith('/'))
        dir.AssertExists()
    

    @classmethod
    def TestExecuteRejectsShellMetacharacters(cls):
        with TESTS.AssertValidation(type=ValidationException):
            UTILS.OS().Execute('echo hello; echo world')


    @classmethod
    def TestExecuteStringCommand(cls):
        ret = UTILS.OS().Execute('echo hello').strip()
        TESTS.AssertEqual(ret, 'hello')
