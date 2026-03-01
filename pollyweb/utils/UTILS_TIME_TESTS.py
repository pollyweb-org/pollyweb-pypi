from .TESTS import TESTS
from .UTILS_TIME import UTILS_TIME



# ✅ DONE
class UTILS_TIME_TESTS(UTILS_TIME):


    @classmethod
    def TestTimer(cls):
        TESTS.AssertNotEqual(cls.Timer(), None)


    @classmethod
    def TestNow(cls):
        TESTS.AssertNotEqual(cls.Now(), None)


    @classmethod
    def TestTimestamp(cls):
        TESTS.AssertNotEqual(cls.GetTimestamp(), None)
    

    @classmethod
    def TestParseTimestamp(cls):
        TESTS.AssertNotEqual(cls.ParseTimestamp('2023-04-01T05:00:30.001000Z'), None)


    @classmethod
    def TestIsNowBetween(cls) -> bool:
        TESTS.Asserts([
            cls.IsNowBetween('2023-04-01T05:00:30.001000Z', '2273-04-01T05:00:30.001000Z') == True,
            cls.IsNowBetween('1913-04-01T05:00:30.001000Z', '2023-04-01T05:00:30.001000Z') == False,
            cls.IsNowBetween('2223-04-01T05:00:30.001000Z', '2373-04-01T05:00:30.001000Z') == False
        ])
        


    @classmethod
    def TestAllTime(cls):
        cls.TestTimer()
        cls.TestNow()
        cls.TestTimestamp()
        cls.TestParseTimestamp()
        cls.TestIsNowBetween()