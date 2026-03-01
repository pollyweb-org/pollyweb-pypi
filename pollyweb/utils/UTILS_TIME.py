# 📚 UTILS

from datetime import datetime, timezone, timedelta
from typing import Union
from .LOG import LOG


# ✅ DONE
class UTILS_TIME: 
    '''👉️ Generic methods.'''


    @classmethod
    def Timer(cls):
        '''👉️ Returns a timer object to measure the duration of procedures.'''
        from .TIMER import TIMER as proxy
        return proxy()


    @classmethod
    def Now(cls) -> datetime:
        '''👉️ Returns the current date-time in UTC.
        * https://stackoverflow.com/questions/67234984/python-get-current-utc-time-ignore-computer-clock-always'''
        dt = datetime.now(timezone.utc)
        #dt = datetime.utcnow()
        return dt
    

    @classmethod
    def Seconds(cls) -> int:
        '''👉️ Returns the current date-time in seconds.'''
        return int(cls.Now().timestamp())
    

    @classmethod
    def SecondsStr(cls):
        '''👉️ Returns the current date-time in seconds as a string.'''
        return str(cls.Seconds())
    

    @classmethod
    def Yesterday(cls) -> datetime:
        '''👉️ Returns yesterday's date-time in UTC.'''
        dt = datetime.now(timezone.utc) - timedelta(1)
        return dt
    

    @classmethod
    def YesterdaysTimestamp(cls) -> str:
        '''👉️ Returns yesterday's date-time in UTC.'''
        return cls.ToTimestamp(cls.Yesterday())
    

    @classmethod
    def Tomorrow(cls) -> datetime:
        '''👉️ Returns tomorrows's date-time in UTC.'''
        dt = datetime.now(timezone.utc) + timedelta(days=1)
        return dt
    

    @classmethod
    def TomorrowsTimestamp(cls) -> str:
        '''👉️ Returns tomorrows's date-time in UTC.'''
        return cls.ToTimestamp(cls.Tomorrow())


    @classmethod
    def Later(cls, seconds:int) -> datetime:
        '''👉️ Returns a later date-time in UTC, after adding seconds.'''
        dt = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        return dt
    

    @classmethod
    def LaterTimestamp(cls, seconds:int) -> str:
        '''👉️ Returns a later timestamp in UTC, after adding seconds.'''
        return cls.ToTimestamp(cls.Later(seconds))


    @classmethod
    def GetTimestamp(cls) -> str:
        '''👉️ Returns a current date-time in UTC format.
        * Source: https://stackoverflow.com/questions/53676600/string-formatting-of-utcnow
        * Usage: UTILS.Timestamp() -> '2023-04-01T05:00:30.001000Z'
        '''
        timestamp = cls.Now().isoformat() + 'Z'
        return timestamp
    

    @classmethod
    def ToTimestamp(cls, dt:datetime) -> str:
        '''👉️ Returns a date-time in UTC format.
        * Source: https://stackoverflow.com/questions/53676600/string-formatting-of-utcnow
        * Usage: UTILS.Timestamp() -> '2023-04-01T05:00:30.001000Z'
        '''
        timestamp = dt.isoformat() + 'Z'
        return timestamp
    
    

    @classmethod
    def ParseTimestamp(cls, date:str) -> Union[datetime, None]:
        '''👉️Parses a UTC date, e.g. 2023-04-01T05:00:30.001000Z
        * https://note.nkmk.me/en/python-datetime-isoformat-fromisoformat/
        ''' 
        if date == None:
            return date
        
        s = date.replace('Z', '')
        
        if '+00:00' not in s:
            s = s + '+00:00'

        dt_utc = datetime.fromisoformat(s)

        return dt_utc


    @classmethod
    def IsNowBetween(cls, start:str, end:str) -> bool:
        '''👉️ Indicates if the current UTC date-time is between 2 UTC date-times.'''
        startDate = cls.ParseTimestamp(start)
        endDate = cls.ParseTimestamp(end)
        now = cls.Now()

        return now >= startDate \
            and (endDate == None or now <= endDate)


    @classmethod
    def IsTimestamp(cls, val:str):
        if not 'Z' in val:
            return False
        
        try:
            cls.ParseTimestamp(val)
            return True
        except:
            return False
        
    
    @classmethod
    def MatchTimestamp(cls, val:Union[str,None]):
        if val == None:
            return
        
        if not 'Z' in val:
            LOG.RaiseValidationException(f'Timestamps must be in UTC (with ending Z, like 2023-04-01T05:00:30.001000Z)! Found=({val})')
        
        # Verify if it's a timestamp.
        noException = False

        try:
            cls.ParseTimestamp(val)
            noException = True
        except:
            pass

        if noException == False:
            LOG.RaiseValidationException(f'Invalid timestamp! Found={val}')
        

    @classmethod
    def GetDuration(cls, start:Union[datetime, str], end:Union[datetime, str]) -> timedelta:
        '''👉️ Returns the duration between 2 date-times.'''
        if type(start) == str:
            start = cls.ParseTimestamp(start)
        if type(end) == str:
            end = cls.ParseTimestamp(end)
        return end - start
    

    @classmethod
    def GetDurationInSeconds(cls, 
        start:Union[datetime, str], 
        end:Union[datetime, str] = None
    ) -> int:
        '''👉️ Returns the duration in seconds between 2 date-times.'''

        if end == None:
            end = cls.Now()

        from .UTILS import UTILS
        UTILS.RequireArgs([start, end])

        duration = cls.GetDuration(start, end)
        return int(duration.total_seconds())
    

    @classmethod
    def Sleep(cls, seconds:int):
        '''👉️ Sleeps for a number of seconds.'''
        from time import sleep
        sleep(seconds)
