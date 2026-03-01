
from typing import Union
from .LOG_EXCEPTION import LOG_EXCEPTION
from .LOG_EXCLUDES import LOG_EXCLUDES
from .PRINTABLE import PRINTABLE


class LOG_BUFFER(PRINTABLE):

    ICON = '📕'


    def __init__(self, 
        path:str,
        deleteFirst:bool=False
    ) -> None:
        '''👉 Creates a new log buffer.
        
        Arguments:
            path {str} -- The path of the file.
        '''

        # Check if we're in a lambda.
        self._isLambda = self.__class__.IsLambda()
        if self._isLambda: return
        
        # Defaults.
        self._logs:list[str] = []
        self._stopped = False
        self._status = 'PENDING'
        self._exceptions:list[LOG_EXCEPTION] = []

        # Validate the path.
        if not path.endswith('.md'):
            raise Exception(
                f'The log path should end in `.md`,'
                f' but received [{path}]')
        
        if '__init__' in path:
            raise Exception(
                f'The log path should not contain `__init__`,'
                f' but received [{path}]')
        
        if '-None.' in path:
            raise Exception(
                f'The log path should not contain `-None.`,'
                f' but received [{path}]')

        # Set the file and folder.
        from .FILESYSTEM import FILESYSTEM
        self._file = FILESYSTEM.FILE(path)
        
        if deleteFirst:
            FILESYSTEM.FILE(path).Delete(safe=True) 
        
        # To avoid bugs, raise an exception if the file already exists.
        if self._file.Exists():
            from .LOG import LOG
            LOG.RaiseValidationException(f'File [{self._file.GetPath()}] already exists.')

        # Create the file and folder, if they don't exist.
        self._file.GetParentDir().Touch()
        self._file.Touch()
        self._file.SetPending()

        # Save the path after chaning the icon.
        self._path = self._file.GetPath()
        self._name = self._file.GetName()
        self._simpleName = self._file.GetSimpleName().split('.')[-1]

        # Setup printable.
        PRINTABLE.__init__(self, toJson=self.ToJson)


    _isLambda = None
    @classmethod
    def IsLambda(cls):
        '''👉 Returns True if the code is running in a Lambda.'''
        if cls._isLambda == None:
            import os
            cls._isLambda = 'AWS_EXECUTION_ENV' in os.environ
        return cls._isLambda
    

    def ToJson(self):
        if self._isLambda: return {}
        return dict(
            Status= self._status,
            File= self._file)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._isLambda: return
        self.LOG().Print(self.__exit__, self)
        self.Stop()
   

    def GetPath(self) -> str:   
        '''👉 Returns the path of the buffer.'''
        if self._isLambda: raise Exception('Cannot get path in lambda.')
        return self._path


    def GetName(self) -> str:
        '''👉 Returns the name of the buffer.'''
        if self._isLambda: raise Exception('Cannot get name in lambda.')
        return self._name
    

    def GetNameWithoutIcon(self) -> str:
        '''👉 Returns the name of the buffer without the icon.'''
        if self._isLambda: raise Exception('Cannot get nameWithoutIcon in lambda.')
        return self._file.GetNameWithoutIcon()
    

    def GetIconName(self) -> str:
        '''👉 Returns the icon and name of the buffer.'''
        if self._isLambda: raise Exception('Cannot get iconName in lambda.')
        return self._file.GetIconName() or ''


    def GetStatus(self) -> str:
        '''👉 Returns the status of the buffer.'''
        if self._isLambda: raise Exception('Cannot get status in lambda.')
        return self._status
    

    def GetLastExceptionName(self) -> str:
        '''👉 Returns the name of the last exception.'''
        if len(self._exceptions) > 0:
            return self._exceptions[-1].GetName()
        return ''


    def Stop(self):
        '''👉 Stops the buffer.
        * The buffer cannot be appended after it is stopped.
        * The icon changes to the status of the buffer.'''
        
        if self._isLambda: return self
        
        if self._stopped:
            return self
        
        self.LOG().Print(self.Stop, self)

        self.DumpToFile()

        # Set the icon on the file, if in the main thread.
        if self.IsDone():
            self._file.SetDone()
        elif self.IsFailed():
            self._file.SetFailed()
        elif self.IsRunning():
            self._file.SetRunning()
        elif self.IsPending():
            self._file.SetPending()

        # Block any further log messages.
        self._stopped = True

        return self


    def IsStopped(self) -> bool:
        '''👉 Returns True if the buffer is stopped.'''
        return self._stopped


    def Append(self, log: Union[str, list[str]]):
        '''👉 Appends a log to the buffer.'''

        if self._isLambda: return self

        if self.IsStopped():
            raise Exception(
                f'Appending to a stopped buffer is not allowed. '
                f'The file name might have been prefixed with an icon.')

        # Append the log as string
        if isinstance(log, str):
            self._logs.append(log)

        elif isinstance(log, list):
            for item in log:
                self._logs.append(item)

        # Raise an exception if the log is not a string or a list of strings
        else:
            raise Exception(f'Invalid log type [{type(log)}]')

        if log:
            if log is str and log.strip() == '':
                pass
            else:
                #title = f'[{self._simpleName}]'  
                #self._logs.append(title)
                pass

        return self


    def GetDir(self):
        '''👉 Returns the __dumps__ folder.'''
        return self._file.GetParentDir()
    

    def _GetFile(self):
        '''👉 Returns the ?.md file.'''
        return self._file
    

    def DumpToFile(self):
        '''👉 Dumps the logs to the LOG.md file.
            * Returns the file object.'''
            
        if self._isLambda: 
            return self
        
        self.LOG().Print(self.DumpToFile, self)

        # If we're in a lambda, don't dump the logs.
        if self._isLambda:
            return "Is Lambda, no file will be created."

        #if self._stopped:
        #    raise Exception('buffer already stopped!')

        from .UTILS import UTILS
        UTILS.AssertIsList(self._logs, itemType=str)

        # Dump the logs to the LOG.md file.
        arr = UTILS.ReverseStrList(self._logs)

        import os
        import threading
        parts = self._name.split(".")
        arr = [
            f'[======START=HEADER===================]',
            f'Name1: {parts[0] if len(parts) > 0 else ""}',
            f'Name2: {parts[1] if len(parts) > 1 and parts[1] != "md" else ""}',
            f'Name3: {parts[2] if len(parts) > 2 and parts[2] != "md" else ""}',
            f'LogBufferStatus: {self._status}',
            f'ProcessID: {os.getpid()}',
            f'ThreadID: {threading.current_thread().ident}',
            f'[=======END=HEADER=====================]',
            f''
        ] + arr
        
        # Create the folder, if if doesn't exist.
        self._file.GetParentDir().Touch()

        if not self._file.Exists():
            self._file.WriteLines(arr)
            
        elif len(arr) > len(self._file.ReadLines()):
            # Only write if we're adding more content.
            # This is because in different processes, the logs might be overwritten.
            self._file.WriteLines(arr)
        
        if not LOG_EXCLUDES.IsExcluded(' LOG.BUFFER'):
            self.LOG().Print('@(): ' 
                f'\nFile: {self._file.GetName()}' 
                f'\nPath: {self._file.GetPath()}')
            
        return self._file


    def ReadText(self):
        return self._file.ReadText()
    

    def ReadLogLines(self):
        '''👉️ Returns the logs of a task.
            * The logs are returned as a list of strings.
            * The logs are reversed.
            * The empty strings are removed.
        '''
        return self._file.ReadLogLines()


    def Clean(self):
        '''👉️ Cleans the buffer file.'''
        
        if self._isLambda: return self

        self.LOG().Print(self.Clean, self)
        self.Delete(reason='cleaning up')
        self._file.Touch()
        self._logs = []
        return self


    def Delete(self, reason:str):
        '''👉️ Deletes the ?.md file with the buffer content.'''

        if self._isLambda: return

        self.LOG().Print(self.Delete, f'{reason=}', self)
        self._file.Delete(safe=True, reason=reason)
        return self
        
    
    def GetLogs(self) -> list[str]:
        '''👉️ Returns the logs of the task.'''
        self.LOG().Print(self.GetLogs)

        ret = self._logs
        from .UTILS import UTILS
        UTILS.AssertIsList(ret, itemType=str)
        return ret
     

    def _SetStatus(self, status:str):
        '''👉️ Sets the status of the current task.'''
        self.LOG().Print(self._SetStatus, f'({status=})', self)
        
        if self._status == 'FAILED':
            self.LOG().Print(self._SetStatus, f': status already failed')
        else: 
            self._status = status

        self.DumpToFile()
        return self


    def SetDone(self):
        if self._isLambda: return

        if self._status == 'DONE':
            return
        self.LOG().Print(self.SetDone)
        self._SetStatus('DONE')

    
    def SetRunning(self):
        if self._isLambda: return

        if self._status == 'RUNNING':
            return
        self.LOG().Print(self.SetRunning, self)
        self._SetStatus('RUNNING')
        

    def SetFail(self, 
        exception:Union[Exception, str, None]=None
    ):
        if self._isLambda: return

        '''👉️ Sets the status to failed.'''
        try:

            self.LOG().Print(self.SetFail, f'({exception=})', self)

            if self._status == 'FAILED':
                self.LOG().Print(self.SetFail, f': status already failed')
                return

            if not exception:
                self.LOG().Print(self.SetFail, f': no exception', self)
                return
            
            self.LOG().Print(self.SetFail, f': has exception')
            if type(exception) == str:
                exception = Exception(exception)
            assert isinstance(exception, Exception)

            try: 
                self.LOG().Print(self.SetFail, f': getting the stack')
                import traceback
                import sys
                
                # Get the current stack.
                #stackTrace = traceback.format_stack()

                # Get the stack of the last exception.
                exc_type, exc_value, exc_traceback = sys.exc_info()
                stackTrace = traceback.format_exception(exc_type, exc_value, exc_traceback)
                stackTrace = stackTrace[:-1]

            except:
                self.LOG().Print(self.SetFail, f': no stack available')
                stackTrace = ['No stack available.']
                
            self.LOG().Print(self.SetFail, f': appending the exception')
            e = LOG_EXCEPTION(
                exception= exception,
                stackTrace= stackTrace)
            
            self._exceptions.append(e)

            self.LOG().PrintException(
                exception= exception,
                stackTrace= stackTrace)
            
        finally:
            self._SetStatus('FAILED')
        

    def IsPending(self) -> bool:
        '''👉️ Returns True if the task is pending.'''
        return self._status == 'PENDING'
    

    def IsRunning(self) -> bool:
        '''👉️ Returns True if the task is running.'''
        return self._status == 'RUNNING'
    

    def IsDone(self) -> bool:
        '''👉️ Returns True if the task is done.'''
        return self._status == 'DONE'
    

    def IsFailed(self) -> bool:
        '''👉️ Returns True if the task is failed.'''
        return self._status == 'FAILED'
    

    def RaiseExceptions(self):
        
        if self.IsFailed():
            for e in self._exceptions:
                raise e._exception
            
        return
        # If the pool has failed, this can happen
        
        if self.IsPending():
            raise Exception(f'Log [{self._file.GetSimpleName()}] is still pending.')
        
        if self.IsRunning():
            raise Exception(f'Log [{self._file.GetSimpleName()}] is still running.')
        

    def GetInfo(self):
        if self._isLambda: raise Exception('Cannot get name in lambda.')

        from .LOG_BUFFER_INFO import LOG_BUFFER_INFO
        return LOG_BUFFER_INFO.New(
            path= self._path,
            name= self._name,
            status= self._status,
            file= self._file)
