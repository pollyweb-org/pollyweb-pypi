class DYNAMO_REAL_TESTS:
    
    ICON = '🧪'


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestDynamoRealCreateTable,
        ]
    

    @classmethod
    def TestDynamoRealCreateTable(cls):
        1/0