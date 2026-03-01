
import pollyweb.utils as pw


class PARALLEL_PROCESS_WRAPPER:

    ICON = '👷'

    
    @classmethod
    def Wrap(cls,
        name:str, 
        handler:callable, 
        args:dict, 
        share:dict, 
        logPath:str,
        writeToConsole:bool,
        testFast:bool,
        onDone:callable
    ):
        '''👉️ Runs inside a child process.'''
      
        # Load imports
        import sys
        sys.path.append('tests/Imports')
        

        #TODO: uncomment
        #from AWS_TEST import AWS_TEST
        #AWS_TEST.SetDomain(domain='*')

        # Create the log buffer.
        log = pw.LOG.PARALLEL().CreateBuffer(path= logPath)
        pw.LOG.PARALLEL().LogProcess(name= name, buffer= log)
        pw.LOG.Settings().SetWriteToConsole(writeToConsole)
        pw.LOG.Settings().SetTestFast(testFast)
        
        # Print the first log message after creating the log buffer. 
        pw.LOG.Print(cls.Wrap, dict(
            name= name,
            handler= handler,
            args= args))
        
        status = 'RUNNING'
        try:
            cls._Run(
                handler= handler, 
                args= args, 
                share= share,
                log= log)
            
            pw.LOG.Print(cls.Wrap, ': executed')
            pw.LOG.Print(cls.Wrap, ': share', dict(share))
            status = 'DONE'

        except Exception as e:
            pw.LOG.Print(cls.Wrap, ': failed', e)
            status = 'FAILED'

        finally:
            pw.LOG.Print(cls.Wrap, ': finally')
            log.Stop()

            if onDone and status == 'DONE':
                onDone(name= name)
        

    @classmethod
    def _Run(cls,
        handler:callable, 
        args:dict, 
        share:dict,
        log:pw.LOG_BUFFER
    ):
        # Invoke the handler
        ret = None
        try:
            
            ret = pw.PYTHON_METHOD(
                handler
            ).InvokeWithMatchingArgs(
                args= args)
            
            pw.LOG.Print(cls._Run, ': done', dict(result= ret))
            
            share['Status'] = 'DONE' 
            log.SetDone()

        except Exception as e:
            share['Status'] = 'FAILED' 
            log.SetFail(e)
            
            try:
                share['ExceptionMessage'] = str(e)
                share['ExceptionType'] = type(e).__name__
            except Exception as e:
                # Potential concurrent exception
                #   AttributeError: 'ForkAwareLocal' object has no attribute 'connection'
                #   During handling of the above exception, another exception occurred:    
                if type(e).__name__ == 'FileNotFoundError:': pass
                if type(e).__name__ == 'AttributeError': pass
                raise
        
        # Return the result.
        pw.LOG.Print(cls._Run, f': returning the result', ret)
        
        try:
            share['Result'] = ret
        except Exception as e:
            # Potential concurrent exception
            if type(e).__name__ == 'FileNotFoundError:': pass
            if type(e).__name__ == 'AttributeError': pass
            raise e
        