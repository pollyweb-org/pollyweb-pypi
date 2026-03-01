class LOG_SETTINGS():
    '''📝️ Settings for the log.'''
    

    def __init__(self):
        self._writeToConsole = False
        '''👉️ If True, writes the log to the console.'''
        self._muteConsole = False
        '''👉️ If True, mutes the console output.'''
        self._pingOnly = None
        self._testFast = False
        '''👉️ If True, disables logs to test in fast mode.'''



    def GetTestFast(self):
        '''👉️ Indicates if logs are disable to test in fast mode.'''
        return self._testFast
    def SetTestFast(self, value:bool= True):
        '''👉️ Disables all logs to test in fast mode.'''
        print(f'📝️ Setting testFast to {value}')
        self._testFast = value


    def GetWriteToConsole(self):
        '''👉️ If True, and not TestFast, writes the log to the console.'''
        return self._writeToConsole and not self._muteConsole
    def SetWriteToConsole(self, value:bool):
        '''👉️ If True, and not MuteConsole, and not TestFast, writes the log to the console.'''
        self._writeToConsole = value
    

    def GetMuteConsole(self):
        return self._muteConsole
    def SetMuteConsole(self, value:bool=True):
        self._muteConsole = value


    def GetPingOnly(self):
        return self._pingOnly
    

    def SetWriteToConsole(self, state:bool=True, pingOnly:bool=False):
        '''👉️ Writes the log to the console.'''
        self._writeToConsole = state
        self._pingOnly = pingOnly


    def GetSettings(self):
        '''👉️ Returns the current settings.'''
        return {
            'writeToConsole': self._writeToConsole,
            'muteConsole': self._muteConsole,
            'pingOnly': self._pingOnly,
            'testFast': self._testFast
        }