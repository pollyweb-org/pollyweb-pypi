class CLOUDFRONT_TESTS:
    
    ICON = '🧪'

    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestCloudfrontRealCreateDistribution,
        ]
    

    @classmethod
    def TestCloudfrontRealCreateDistribution(cls):
        1/0