class CODEPIPELINE_TESTS:
    
    ICON = '🧪'

    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestCodepipelineRealCreatePipeline,
        ]
    

    @classmethod
    def TestCodepipelineRealCreatePipeline(cls):
        1/0