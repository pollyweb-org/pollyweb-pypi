import threading
from typing import Union
from .LOG_BUFFER import LOG_BUFFER


class LOG_PARALLEL:

    _processBuffers:list[LOG_BUFFER] = []
    _threadBuffers:dict[str,list[LOG_BUFFER]] = {}


    @classmethod
    def LOG(cls):
        '''👉️ Logs to the parallel buffers.'''
        from .LOG import LOG
        return LOG


    @classmethod
    def _GetCurrentThreadID(cls):
        '''👉️ Returns the ID of the current thread.'''
        return threading.current_thread().ident


    @classmethod
    def GetParallelLogDir(cls):
        '''👉️ Get the PARALLEL log directory.'''
        dir = cls.LOG().GetLogDir().Touch().GetSubDir('PARALLEL').Touch()
        return dir


    @classmethod
    def CreateBuffer(cls, 
        name:str= None, 
        path:str= None,
        goUp:int= 0
    ) -> LOG_BUFFER:
        '''👉️ Creates a buffor to be attached later.
         
        Arguments:
            
            `name` {str} -- Optional suffix of the buffer's file, 
                to be added to {class}.{method} of the caller
                    useful when reusing the same method.

            `goUp` {int} -- Optional number of levels to go up to get the caller's name.
                useful when the method is called from a wrapper.

        Usage:
            ```python
            buffer = LOG.PARALLEL().CreateBuffer() 
            ```
        '''
        from .UTILS import UTILS
            
        if path == None:
            # Get the caller's full name.
            caller_name = UTILS.GetCallerFullName(goUp=goUp+1) 
            
            # Get the path of the buffer.
            name = f'.{name}' if name else ''
            path = f'{caller_name}{name}.md'
        
        for forbiden in [
            '__init__',
            'DEPLOYER_MAESTRO_PARALLEL.',
            'PARALLEL.',
            'LOG_PARALLEL.',
            '_WorkItem.run.',
        ]:
            if forbiden in path:
                cls.LOG().RaiseException(
                    f'Log path cannot contain ({forbiden}). ',
                    '👉 Increase the GetCallerFullName() up level.'
                    f'\nGiven [{path}]')
                      
        path = path.replace('.None.', '.')
        file = cls.GetParallelLogDir().GetFile(path)
        path = file.GetPath()

        if file.Exists():
            cls.LOG().RaiseException(
                f'File [{path}] already exists.')

        # Create the buffer.
        buffer = LOG_BUFFER(path)
        
        return buffer


    @classmethod
    def LogProcess(cls, 
        name:str=None, 
        buffer:LOG_BUFFER=None,
        goUp:int=0
    ):
        '''👉️ Creates a buffer for the current process.
            * To create a buffer without attaching it, use `CreateBuffer()`.
            * To create a buffer for a thread, use `LogThread()`.
        
        Arguments:

            `name` {str} -- Optional suffix of the buffer's file, 
                to be added to {class}.{method} of the caller
                    useful when reusing the same method.

            `buffer` {LOG_BUFFER} -- Optional buffer to append to.
                if not given, a new buffer is created.
                    useful to create the buffer before the thread/process.

            `goUp` {int} -- Optional number of levels to go up to get the caller's name.
                useful when the method is called from a wrapper.

        Usage:
            ```python
            buffer = LOG.PARALLEL().LogProcess()    
            ```
        '''
        
        if not buffer:
            buffer = cls.CreateBuffer(
                name= name, 
                goUp= goUp+1)
        
        # Append to the process buffers.
        if buffer.GetPath() in [b.GetPath for b in cls._processBuffers]:
            cls.LOG().RaiseException(
                f'Buffer [{buffer.GetName()}] already exists.')
        cls._processBuffers.append(buffer)

        return buffer


    @classmethod
    def LogThread(cls, 
        buffer:LOG_BUFFER=None, 
        name:str='',
        path:str=None,
        goUp:int=0
    ):
        '''👉️ Creates a buffer for the current thread.'''

        # This is not doing anything, at the moment.
        threading.current_thread().name = name

        if not buffer:
            buffer = cls.CreateBuffer(
                name= name,
                path= path,
                goUp= goUp+1)
            
        # Append to the thread buffers.
        threadID = cls._GetCurrentThreadID()
        if threadID not in cls._threadBuffers:
            cls._threadBuffers[threadID] = []
        cls._threadBuffers[threadID].append(buffer)

        return buffer


    @classmethod
    def GetCurrentBuffers(cls):
        '''👉️ Returns the active buffers.'''

        ret:list[LOG_BUFFER] = []

        # Append to all buffers listening to the process.
        for p in cls._processBuffers:
            if not p.IsStopped():
                ret.append(p)

        # Find the buffers of the current thread.
        threadID = cls._GetCurrentThreadID()
        if threadID in cls._threadBuffers:

            # Append to all buffers in the current thread.
            for t in cls._threadBuffers[threadID]:
                if not t.IsStopped():
                    ret.append(t)

        return ret


    @classmethod
    def _DumpToFile(cls):
        '''👉️ Dumps the parallel buffers to the log files.'''

        for b in cls.GetCurrentBuffers():
            if not b.IsStopped():
                b.DumpToFile()


    @classmethod
    def StopBuffers(cls):
        '''👉️ Stops all the buffers.'''

        for b in cls.GetCurrentBuffers():
            if not b.IsStopped():
                b.Stop()
        

    @classmethod
    def _AppendParallel(cls, log:Union[str, list]):
        '''👉️ Appends a log to the parallel buffers.'''

        appended:list[str] = []

        # Append to all buffers listening to the process.
        for p in cls._processBuffers:
            path = p.GetPath()
            if path in appended:
                continue
            elif p.IsStopped():
                continue
                # TODO: Remove stopped processes.
                #cls._processBuffers.remove(p)
            else:
                p.Append(log)
                appended.append(p.GetPath())

        # Find the buffers of the current thread.
        threadID = cls._GetCurrentThreadID()
        if threadID in cls._threadBuffers:

            # Append to all buffers in the current thread.
            for t in cls._threadBuffers[threadID]:
                path = t.GetPath()
                if path in appended:
                    continue
                elif t.IsStopped():
                    # Remove stopped threads.
                    cls._threadBuffers[threadID].remove(t)
                else:
                    t.Append(log)
                    appended.append(t.GetPath())


    @classmethod    
    def _DeleteParallel(cls):
        '''👉️ Deletes the PARALLEL logs directory.'''
        cls.GetParallelLogDir().Delete(recursive=True)


    @classmethod 
    def SetMethodDone(cls, 
        method:str=None,
        dirName:str=None,
        goUp:int=0
    ):
        '''👉️ Collapses the PARALLEL directory.'''

        from .LOG import LOG
        from .UTILS import UTILS
        from .FILE import FILE
        from .PYTHON_METHOD import PYTHON_METHOD

        # Dump all the buffers.
        cls.StopBuffers()

        # Calculate the dir's name
        if dirName:
            dir = LOG.PARALLEL().GetParallelLogDir().GetSubDir(dirName)
        else:
            if method:
                dirName = PYTHON_METHOD(method).GetFullName()
            else:
                dirName = UTILS.GetCallerFullName(goUp=goUp+1) 
            dir = cls.GetParallelLogDir().GetSubDir(dirName)

        # Create the dir.
        dir.Touch()
        dir.SetDone()

        # Move the child logs to the new dir.
        files:list[FILE] = [] 
        for file in cls.GetParallelLogDir().GetFiles():
            if file.GetNameWithoutIcon().startswith(f'{dirName}.'):
                files.append(file)

        if len(files) == 0:
            cls.LOG().Print(cls.SetMethodDone,
                f'No log files found starting with [{dirName}].')
            return

        for file in files:
            file.MoveTo(dir)

        return dir


    @classmethod 
    def SetClassDone(cls, 
        clas:type= None,
        goUp:int= 0,
        validator:callable= None
    ):
        '''👉️ Collapses the parallel directory.
        
        Arguments:
            * `clas` {type} -- Optional class to collapse.
                If not given, the caller's class is used.
            * `goUp` {int} -- Optional number of levels to go up to get the caller's name.
                Useful when the method is called from a wrapper.
            * `validator` {callable} -- Optional validator to check the files.
                Useful to keep the paths valid in the stack trace dump.
        '''

        import os
        import shutil

        from .UTILS import UTILS

        # Get the class name.
        if clas != None:
            from .PYTHON_CLASS import PYTHON_CLASS
            class_name = PYTHON_CLASS(clas).GetName()
        else:
            class_name = UTILS.GetCallerClassName(goUp= goUp+1)

        # Group the children.
        from .FILESYSTEM_OBJECT import FILESYSTEM_OBJECT
        children:dict[str,FILESYSTEM_OBJECT] = {}

        for subDir in cls.GetParallelLogDir().GetSubDirs():
            name = subDir.GetNameWithoutIcon()
            # Skip the current class
            if name == class_name:
                continue
            # Add the children called class_name*
            if name.startswith(f'{class_name}'):
                children[subDir.GetName()] = subDir

        for file in cls.GetParallelLogDir().GetFiles():
            if file.GetNameWithoutIcon().startswith(f'{class_name}.'):
                children[file.GetName()] = file

        if validator:
            validator(children)

        # Create the dir.
        dir = cls.GetParallelLogDir().GetSubDirIconned(class_name)
        dir.Touch()
        dir.SetDone()

        # Move the child logs to the new dir.
        for key, obj in children.items():
            target = os.path.join(dir.GetPath(), obj.GetName())
            if os.path.isdir(target):
                shutil.rmtree(target, ignore_errors=True)
            elif os.path.isfile(target):
                try:
                    os.remove(target)
                except FileNotFoundError:
                    pass
            obj.MoveTo(dir)

        # Remove the directory if empty (no testes executed).
        if len(dir.GetFiles()) == 0:
            try:
                dir.Delete()
                pass
            except:
                # Survive concurrency.
                pass

        return dir
