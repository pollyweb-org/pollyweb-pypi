import PW_UTILS as pw
from .PARALLEL import PARALLEL


class PARALLEL_LOG_TESTS:

    ICON = '🧪'


    @classmethod
    def thread_function(cls, 
        name:str, 
        results:dict, 
        fn:callable, 
        kargs:dict
    ):
        
        try:
            pw.PYTHON_METHOD(fn).InvokeWithMatchingArgs(kargs)

            results[name] = {
                'Status': 'Done',
            }
        except Exception as e:
            results[name] = {
                'Status': 'Exception',
                'Exception': e,
            }

    
    @classmethod
    def _CommonRunTask(cls, 
        name:str, 
        fn:callable, 
        kargs:dict
    ):

        import threading
        results:dict = {}

        thread = threading.Thread(
            name= name,
            target= cls.thread_function, 
            args= (name, results, fn, kargs))
        
        thread.start()
        thread.join()  # Wait for the thread to complete
        
        if pw.STRUCT(results).RequireStruct(name).RequireStr('Status') == 'Exception':
            raise results[name]['Exception']


    @classmethod
    def TestParallelLog(cls):
        pw.LOG.Print('🧪‍ PARALLEL_LOG_TESTS.TestParallelLog()')

        buffers:dict[str, pw.LOG_BUFFER] = {}

        # Print on an unkown thread.
        pw.LOG.Print('Unkown running') 
        
        # Print on the main thread.
        with pw.LOG.LogProcess(
            name='TestParallelLog') as processBuffer:

            buffers[cls.TestParallelLog.__name__] = processBuffer

            pw.LOG.Print('Main running')

            # Print on a task.
            def _MyThreadFunction(
                name:str, 
                success:bool|None=None, 
                threadBuffer:pw.LOG_BUFFER=None
            ):
                pw.LOG.LogThread(threadBuffer)
                pw.LOG.Print(f'{name} running')
                
                if success == True: 
                    threadBuffer.SetDone()
                elif success == False:
                    threadBuffer.SetFail('Task failed')
                else:
                    pass


            def _MyRunTask(name:str, success:bool=None):
                with pw.LOG.CreateBuffer(name) as threadBuffer:
                    buffers[name] = threadBuffer

                    # Execute the task.
                    cls._CommonRunTask(
                        name= name, 
                        fn= _MyThreadFunction, 
                        kargs=dict(
                            name= name, 
                            success= success, 
                            threadBuffer= threadBuffer))

                    # Assert the registered threads.
                    if not pw.LOG.Settings().GetTestFast():
                        pw.TESTS.AssertNotEqual(
                            threadBuffer.GetLogs(), [])
                        pw.UTILS.AssertContains(
                            lst= threadBuffer.GetLogs(), 
                            value= f'{name} running')

            _MyRunTask('TaskRunning')
            _MyRunTask('TaskSuccessed', True)
            _MyRunTask('TaskFailed', False)

            # Stop parallel logging.
        pw.LOG.Print('Unkown stopped') 

        # Dump the logs.
        buffers[cls.TestParallelLog.__name__].DumpToFile()
        main = pw.LOG.Buffer()

        # Assert the main location.
        main.GetDir().AssertName('__dumps__')

        # Read the main content.
        main.DumpToFile()
        if not pw.LOG.Settings().GetTestFast():
            lines = main.ReadLogLines()
            if lines == []:
                pw.LOG.RaiseException(
                    f'Empty log file,'
                    f' - did you forget to Dump the file?', main)
        
        # Check the main log content.
        if not pw.LOG.Settings().GetTestFast():
            pw.TESTS.AssertTrue(
                pw.UTILS.ContainsAll(
                    lines, [ 
                        'Unkown running',
                        'Main running'  ,
                        'TaskRunning running',
                        'TaskSuccessed running',
                        'TaskFailed running',
                        'Unkown stopped'
                    ]))
        
        # Get a main task
        processLog = buffers[cls.TestParallelLog.__name__]
        
        # Assert the main task location.
        processLog.GetDir().AssertName('PARALLEL')
        nameBeforeUuid = processLog.GetNameWithoutIcon().split('[')[0]
        pw.TESTS.AssertEqual(nameBeforeUuid, 
                f'{PARALLEL_LOG_TESTS.__name__}.'
                f'{cls.TestParallelLog.__name__}.'
                f'{cls.TestParallelLog.__name__}.md')
        pw.TESTS.AssertFalse(
            processLog.GetName().endswith('].md'))
        
        if not pw.LOG.Settings().GetTestFast():
            pw.TESTS.AssertTrue(
                pw.UTILS.ContainsAll(
                    processLog.ReadLogLines(), [
                        'Main running'
                    ]))

        # Get a sub task
        successTaskLog = buffers['TaskSuccessed']      
        nameBeforeUuid = successTaskLog.GetNameWithoutIcon().split('[')[0]  
        pw.TESTS.AssertEqual(nameBeforeUuid,
            f'{PARALLEL_LOG_TESTS.__name__}.'
            f'{PARALLEL_LOG_TESTS.TestParallelLog.__name__}.'
            f'TaskSuccessed.md')

        # Assert the failed task.
        failedTaskLog = buffers['TaskFailed']
        failedTaskLog.GetDir().AssertName('PARALLEL')

        # Check the failed task log content.
        if not pw.LOG.Settings().GetTestFast():
            logs = failedTaskLog.ReadLogLines()
            pw.TESTS.AssertEqual(logs[0], 'TaskFailed running')

        taskRunningLog = buffers['TaskRunning']
        if not pw.LOG.Settings().GetTestFast():
            pw.UTILS.AssertContains(
                lst= taskRunningLog.ReadLogLines(), 
                value= 'TaskRunning running')
        
        taskSuccessedLog = buffers['TaskSuccessed']
        if not pw.LOG.Settings().GetTestFast():
            pw.UTILS.AssertContains(
                lst= taskSuccessedLog.ReadLogLines(), 
                value= 'TaskSuccessed running')
        
        # Delete the logs.
        for buffer in buffers.values():
            buffer.Delete(reason='TestParallelLog()')
            pass
        