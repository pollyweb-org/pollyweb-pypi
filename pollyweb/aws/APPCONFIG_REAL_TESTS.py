from APPCONFIG_REAL_DEPLOY import APPCONFIG_REAL_DEPLOY
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from LOG import LOG


class APPCONFIG_REAL_TESTS(AWS_RESOURCE_TESTER):
    
    ICON = '🧪'


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.CreateDelete,
        ]
    

    @classmethod
    def CreateDelete(cls):
        NAME= 'NLWEB-TEST'
        appConfig = APPCONFIG_REAL_DEPLOY()
        
        app = appConfig.GetApp(name= NAME)
        if app:
            app.Delete()

        app = appConfig.CreateApp(name= NAME)
        app.Delete()

        app = appConfig.GetApp(name= NAME)
        if app:
            LOG.RaiseException('App should have been deleted!')