import pollyweb.utils as pw


class PARALLEL():


    @classmethod
    def GetLogDir(cls):
        '''👉️ Returns the parallel directory.'''
        return pw.LOG.GetLogDir().GetSubDir('PARALLEL').Touch()


    @classmethod
    def DISPLAY(cls):
        '''👉️ Returns the parallel display.'''
        from .PARALLEL_DISPLAY import PARALLEL_DISPLAY
        return PARALLEL_DISPLAY()
   

    @classmethod
    def PROCESS_POOL(cls, 
        name:str= None,
        seconds:int= None,
    ):
        '''👉️ Returns the parallel process pool.'''
        from .PARALLEL_PROCESS_POOL import PARALLEL_PROCESS_POOL
        return PARALLEL_PROCESS_POOL(name=name, goUp=1)


    @classmethod
    def THREAD_POOL(cls, 
        seconds:int=None,
        maxWorkers:int=30,
        continueMethod:callable=None,
        name:str= None,
        goUp:int=0
    ):
        '''👉️ Returns the parallel runner.'''

        from .PARALLEL_THREAD_POOL import  PARALLEL_THREAD_POOL
        ret = PARALLEL_THREAD_POOL(
            name= name,
            maxWorkers= maxWorkers,
            continueMethod= continueMethod,
            seconds= seconds,
            goUp= goUp+1)
        return ret
    
    
