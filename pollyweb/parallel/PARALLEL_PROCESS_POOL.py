from .PARALLEL_PROCESS import PARALLEL_PROCESS



import PW_UTILS as pw


class PARALLEL_PROCESS_POOL(pw.PRINTABLE):
    '''👉️ A pool of processes.'''

    ICON = '🏭'


    def __init__(self, 
        name:str=None, 
        onDone:callable=None,
        goUp:int=0
    ) -> None:
        '''👉️ Initialize the process pool.'''
        
        # Set the name.
        self._name = name
        self._onDone = onDone

        # The dictionary of processes, indexed by name.
        self._processesByName:dict[str,PARALLEL_PROCESS] = {}

        self._log = pw.LOG.PARALLEL().LogProcess(
            name= name,
            goUp=goUp+1) 
        
        self._exited = False

        # This should be the last line.
        super().__init__(self.ToJson)


    def __enter__(self):
        '''👉️ Auxiliar method to run with:.'''
        pw.LOG.Print(self.__enter__, self)
        self._entered = True
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        '''👉️ Close all processes when exiting the with:.'''
        
        pw.LOG.Print(self.__exit__, f'({self._log.GetName()})', self)

        if self._exited: return 
        
        # Wait for all processes to finish or error.
        try:
            results = self.GetResults()
            pw.LOG.Print(self.__exit__, f': results=', results, self)

            # Update the status.
            if self.HasFailedProcesses():
                self.GetLog().SetFail()
            else:
                self.GetLog().SetDone()

        except Exception as e:
            self.GetLog().SetFail(e)

        # Stop the log and dump it to file.
        self._log.Stop()

        self._exited = True
        
        self.RaiseExceptions()


    def RaiseExceptions(self):
        '''👉️ Raise any exceptions.'''
        for p in self.GetProcessList():
            p.RaiseException()


    def HasFailedProcesses(self) -> bool:
        '''👉️ Returns True if any process failed.'''
        for p in self.GetProcessList():
            if p.HasException():
                return True
        return False


    def GetProcessList(self) -> list[PARALLEL_PROCESS]:
        return [
            value
            for key, value in self._processesByName.items()
        ]


    def GetName(self) -> str:
        '''👉️ Return the name of the process pool.'''
        return self._name


    def GetProcessCount(self) -> int:
        '''👉️ Return the number of processes.'''
        return len(self._processesByName.keys())


    def GetLog(self):
        '''👉️ Returns the log buffer.'''
        pw.LOG.Print(self.GetLog)
        return self._log


    def ToJson(self) -> dict[str, any]:
        '''👉️ Return the JSON representation of the object.'''
        return dict(
            Name= self._name,
            Processes= self._processesByName, 
            Status= self._log.GetStatus(),
            Log= self._log.GetName())


    def RunProcessList(self, 
        handlers:list[callable], 
        parallel:bool= True,
        goUp:int=0
    ):
        pw.LOG.Print(self.RunProcessList)

        # Run the processes in sequence.
        if not parallel:
            for handler in handlers:
                pw.PYTHON_METHOD(
                    handler
                ).InvokeWithMatchingArgs(
                    args= dict(pool= self),
                    optional=['pool'])
            return

        # Run the processes in parallel.
        with self:
            for handler in handlers:
                self.StartProcess(
                    name = f'{handler.__name__}',
                    handler= handler, 
                    goUp= goUp+1)
            return self.GetResults()


    def RunProcess(self, 
        handler:callable, 
        args:dict|None = None,
        goUp:int=0
    ) -> any:
        '''👉️ Run a process and wait for it to finish.'''
        
        pw.LOG.Print(self.RunProcess)

        with self:
            with self.StartProcess(
                name = f'{handler.__name__}',
                handler= handler, 
                args= args if args is not None else {},
                goUp= goUp+1
            ) as p:
                return p.GetResult()


    def StartProcessList(self,
        handlers:list[callable],
        parallel:bool=True, 
        goUp:int=0
    ):
        '''👉️ Start a list of processes.'''
        pw.LOG.Print(self.StartProcessList)

        # Run the processes in sequence.
        if not parallel:
            for handler in handlers:
                
                print(f'\n🏃 Running: {handler.__name__}')
                pw.LOG.DumpToFile()

                pw.PYTHON_METHOD(
                    handler
                ).InvokeWithMatchingArgs(
                    args= dict(pool= self),
                    optional=['pool'])
            return
        
        for handler in handlers:
            self.StartProcess(
                name = f'{handler.__name__}',
                handler= handler, 
                goUp= goUp+1)


    def StartProcess(self, 
        handler:callable, 
        args:dict|None = None,
        name:str = None,
        onDone:callable = None,
        goUp:int = 0
    ) -> PARALLEL_PROCESS:
        '''👉️ Start a process and return it.
        * handler: The function to run.
        * args: The arguments to pass to the function.
        * name: The name of the process (defaults to the name of the handler).
        '''

        pw.LOG.Print(self.StartProcess, handler)

        if not hasattr(self, '_entered') or not self._entered:
            pw.LOG.RaiseException(
                'The process pool should be used with a `with` statement. '
                'Or use the `RunProcess` method.')
            
        self._log.SetRunning()
               
        # Create the process.
        p = PARALLEL_PROCESS(
            name= name,
            handler= handler,
            args= args if args is not None else {},
            pool= self,
            onDone= onDone,
            goUp= goUp+1)
        
        # See if the name was replaced by the handler's name.
        pw.LOG.Print(self.StartProcess, f': Process created', p)
        name = p.GetName()
        if name is None:
            name = f'{handler.__name__}'

        # Check if the process already exists.
        if name in self._processesByName:
            pw.LOG.RaiseException(f'Process {name} already exists.')
        else:
            self._processesByName[name] = p

        p.Start()
        return p


    def GetResults(self) -> dict[str, any]:
        '''👉️ Join all processes.'''

        pw.LOG.Print(self.GetResults)

        ret = {}

        keys = list(self._processesByName.keys())
        for name in keys:

            # Get the process from the process dictionary.
            p = self._processesByName[name]

            # Join the process to wait until the result is ready.
            result = p.Join()
            ret[name] = result

            pw.LOG.Print(self.GetResults, f': Process [{name}] joined', p)
            
        pw.LOG.Print(self.GetResults, f': results=', ret)
        return ret
