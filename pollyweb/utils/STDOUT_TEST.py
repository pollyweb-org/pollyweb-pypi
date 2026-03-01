from .STDOUT import STDOUT
from .TESTS import TESTS

class STDOUT_TEST:
    
    
    @classmethod
    def TestAllStdOut(cls):

        STDOUT.Capture()

        # Print something
        print("Hello world!")
        print("Another line")

        ret = STDOUT.Release()
        TESTS.AssertEqual(ret, "Hello world!\nAnother line\n",
                         "Captured output does not match expected.")
        
        ret = STDOUT.GetAllLines()
        TESTS.AssertEqual(ret, "Hello world!\nAnother line\n",
                         "GetAllLines output does not match expected.")
        
        ret = STDOUT.GetLastLine()
        TESTS.AssertEqual(ret, "Another line",
                         "GetLastLine output does not match expected.") 
