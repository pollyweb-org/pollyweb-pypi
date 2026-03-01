# 📚 TIMER

import datetime

def test():
    return 'this is a TIMER test.'


class TIMER:

    def __init__(self) -> None:
        self.timerStart = datetime.datetime.now()

    def Elapsed(self):
        global timerStart
        current = datetime.datetime.now()
        elapsed = (current - self.timerStart)
        timerStart = current
        output = round(elapsed.total_seconds() * 1000)
        return f'''--> Elapsed: {output} ms
    .
    '''

    def PrintElapsed(self):
        ##LOG.Print(f"--- {self.Elapsed()} milliseconds elapsed")
        pass

       
    def StartWatch(self):
        return datetime.datetime.now()


    def StopWatch(self, start:datetime.datetime):
        current = datetime.datetime.now()
        elapsed:datetime.timedelta = (current - start)
        output = round(elapsed.total_seconds() * 1000)
        return f'{output} ms'


    