
from .LOG import LOG
from .TESTS import TESTS
from .UTILS import UTILS

class LOG_TESTS(LOG):

    ICON= '📜'
    

    @classmethod
    def TestPrintStructures(cls):

        # Test text.        
        LOG._PrintInternal(isLambda=False, msg= 'Text')
        LOG._PrintInternal(isLambda=True, msg= 'Text')

        # Test none.
        LOG._PrintInternal(False, None, None)
        LOG._PrintInternal(True, None, None)
        LOG._PrintInternal(False, type(None), type(None))
        LOG._PrintInternal(True, type(None), type(None))
        
        LOG._PrintInternal(False,'', 
            f'{None=}', f'{None=}', f'{None=}',
            f'body=', None)
        
        LOG._PrintInternal(True,'', 
            f'{None=}', f'{None=}', f'{None=}',
            f'body=', None)

        # Test dictionaries.
        LOG._PrintInternal(False, {'A', 1}, [{'A', 1}])
        LOG._PrintInternal(True, {'A', 1}, [{'A', 1}])

        # Test types.
        LOG._PrintInternal(False, str, str)
        LOG._PrintInternal(True, set, set)
        
        # Test tuples.
        LOG._PrintInternal(False, (1,2), (1,2))
        LOG._PrintInternal(True, (1,2), (1,2))

        # Test dates.
        from datetime import datetime
        LOG._PrintInternal(False, datetime.now(), [datetime.now()])
        LOG._PrintInternal(True, datetime.now(), [datetime.now()])

        LOG.Print('Text', {'A': 1})
        LOG.Print({'A', 'B'})

        # Test exceptions.
        try:
            raise Exception('Test Exception')
        except Exception as e:
            LOG.Print('Error', e)



    @classmethod
    def TestPrintToConsole(cls):
        '''👉️ Test the print to console.'''
        
        from .STDOUT import STDOUT
        STDOUT.Capture()

        # save the current settings.
        _muteConsole = LOG.Settings()._muteConsole
        _writeToConsole = LOG.Settings()._writeToConsole 
        _testFast = LOG.Settings()._testFast

        # Set the settings to print to console.
        LOG.Settings()._muteConsole = False
        LOG.Settings()._writeToConsole = True
        LOG.Settings()._testFast = False
        
        # Test printing to console.
        LOG.Print(cls.TestPrintToConsole, 'This is a test message.')
        
        # Check the output.
        output = STDOUT.Release()
        LOG.Print(cls.TestPrintToConsole, f'Captured output= `{output}`', )

        TESTS.AssertContainsStr(output, 'LOG_TESTS.TestPrintToConsole()', 
            msg= 'Output should contain the test method name.')
        
        # In the console, the message details should not be printed.
        with TESTS.AssertValidation():
            TESTS.AssertContainsStr(output, 'This is a test message.', 
                msg= 'Output should contain the printed message.')

        # Restore the settings.      
        LOG.Settings()._muteConsole = _muteConsole
        LOG.Settings()._writeToConsole = _writeToConsole
        LOG.Settings()._testFast = _testFast
    

    @classmethod
    def TestAllLogs(cls):
        '''👉️ Test the logs.'''
        
        cls.TestPrintStructures()
        cls.TestPrintToConsole()
