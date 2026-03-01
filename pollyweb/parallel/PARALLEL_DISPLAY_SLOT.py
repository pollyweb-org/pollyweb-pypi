import PW_UTILS as pw


class PARALLEL_DISPLAY_SLOT(pw.STRUCT):

    sequenceCounter = 0

    def __init__(self, id:int):
        super().__init__({
            'ID': id,
            'Status': 'FREE',
            'Sequence': 0
        })
        

    def GetID(self):
        return self.RequireInt('ID')


    def IsFree(self):
        status = self.RequireStr('Status')
        return status == 'FREE' or status == 'DONE'
    

    def GetSequence(self):
        return self.RequireInt('Sequence')
    

    def Start(self, description:str):
        self['Status'] = 'RUNNING'

        # Assign a sequence number, or use older finished slots first.
        PARALLEL_DISPLAY_SLOT.sequenceCounter += 1
        self['Sequence'] = PARALLEL_DISPLAY_SLOT.sequenceCounter 

        slot = self.GetID()
        print(f"\033[{slot};0H\033[K\033[33m[{slot}] {description}...\033[0m", end='', flush=True)


    def Finish(self, description:str):
        self['Status'] = 'DONE'
        slot = self.GetID()
        print(f"\033[{slot};0H\033[K\033[32m[{slot}]: {description}!\033[0m", end='', flush=True)


    def Fail(self, 
        description:str, 
        exception:Exception, 
        stackTrace:str
    ):
        try:
            if exception is not None:
                self.stackTrace = stackTrace
                self.exception = exception
                self['ErrorMessage'] = [str(exception)]
                self['ErrorType'] = type(exception).__name__
        except Exception as capture_error:
            self.stackTrace = stackTrace
            self.exception = exception if exception is not None else capture_error
            self['ErrorMessage'] = [str(capture_error)]
            self['ErrorType'] = type(capture_error).__name__

        self['Status'] = 'ERROR'
        slot = self.GetID()
        print(
            f"\033[{slot};0H\033[K\033[31m[{slot}]: {description} - {str(exception)}\033[0m", 
            end='', flush=True)


    def IsFailed(self):
        return self['Status'] == 'ERROR'


    def RaiseException(self):
        if self.IsFailed():
            raise self.exception
