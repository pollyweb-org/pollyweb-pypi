
import datetime

class LOG_PLACEHOLDER:


    def __init__(self):
        self._lastPing:datetime.datetime = datetime.datetime.now()


    def Ping(self):
        # ping only once in a while.
        elapsed = (datetime.datetime.now() - self._lastPing)
        if elapsed.total_seconds() > 0.1:
            print('.', end='', flush=True)
            self._lastPing = datetime.datetime.now()