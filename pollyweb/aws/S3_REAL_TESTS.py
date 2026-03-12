class S3_REAL_TESTS:
    
    ICON = '🧪'


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestS3RealCreateBucket,
        ]
    

    @classmethod
    def TestS3RealCreateBucket(cls):
        1/0