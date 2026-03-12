class EVENTBRIDGE_REAL_TESTS:
    ICON = '🧪'


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestEventBridgeRealPutEvents,
        ]
    

    @classmethod
    def TestEventBridgeRealPutEvents(cls):
        1/0


