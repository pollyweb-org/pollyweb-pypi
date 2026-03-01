from .LOG_BUFFER import LOG_BUFFER
from .TESTS import TESTS

class LOG_BUFFER_TEST:
    

    @classmethod
    def TestAllLogBuffer(cls):
        
        path = 'test_log_buffer.md'
        
        # Create the log buffer (in memory).
        buffer = LOG_BUFFER(
            path= path, 
            deleteFirst= True)
        
        # Make sure the file now exists.
        buffer._GetFile().AssertExists()

        # Append some lines to the log buffer in memory.
        buffer.Append('First line.')
        buffer.Append('Second line.')

        # Write the log buffer to the file.
        buffer.DumpToFile()

        # read the file and check its contents.
        dumpedFile = buffer._GetFile().ReadLines()        

        # Check if contents are backwards.
        TESTS.AssertEqual(
            given= dumpedFile[-2:], 
            expect= ['Second line.', 'First line.'])
        
        # Clean up the file.
        buffer.Clean()
        TESTS.AssertEqual(
            given= buffer._GetFile().ReadLines(), 
            expect= [])
        
        # Delete the file
        buffer._GetFile().Delete()
                