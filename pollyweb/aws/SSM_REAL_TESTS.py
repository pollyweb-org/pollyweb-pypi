class SSM_REAL_TESTS:
    ICON = '🧪'


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestSsmRealCreateParameter,
        ]
    

    @classmethod
    def TestSsmRealCreateParameter(cls):
        1/0