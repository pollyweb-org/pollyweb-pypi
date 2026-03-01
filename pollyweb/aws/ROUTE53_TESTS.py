class ROUTE53_TESTS:
    ICON = '🧪'


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestRoute53RealCreateHostedZone,
        ]
    

    @classmethod
    def TestRoute53RealCreateHostedZone(cls):
        1/0