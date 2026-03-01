import sys
import io


class STDOUT:
    """A class to handle standard output operations."""

    @classmethod
    def Capture(cls):
        '''Capture the standard output to a buffer for testing purposes.
        - After capturing, you can print to the console and then release the output.
        - Call `Release()` to restore the original stdout and get the captured output.'''
            
        # Save original stdout
        cls.original_stdout = sys.stdout

        # Redirect stdout to a buffer
        cls.buffer = io.StringIO()
        sys.stdout = cls.buffer



    @classmethod
    def Release(cls):
        """Release the captured output and restore stdout."""

        # Restore stdout
        sys.stdout = cls.original_stdout

        # Get captured output
        cls.captured_output = cls.buffer.getvalue()
        cls.buffer.close()

        return cls.captured_output


    @classmethod
    def GetAllLines(cls):
        """Capture the output, print something, and then release it."""
        if not hasattr(cls, 'captured_output'):
            return None
        return cls.captured_output
        

    @classmethod
    def GetLastLine(cls):
        """Get the latest line from the captured output."""
        if not hasattr(cls, 'captured_output'):
            return None

        # Get only the latest line
        latest_line = cls.captured_output.strip().split("\n")[-1]
        return latest_line


    @classmethod
    def Test(cls):

        cls.Capture()

        # Print something
        print("Hello world!")
        print("Another line")

        cls.Release()
        