from AWS import AWS
from pollyweb.utils.TESTS import TESTS
from pollyweb.utils.UTILS import UTILS


class SECRETS_REAL_TESTS:


    @classmethod
    def GetAllTests(cls):
        return [
            cls.Secrets,
        ]
    

    @classmethod
    def Secrets(cls):
        secrets = AWS.SECRETS()
        name= f'/NLWEB/{UTILS.UUID()}'
        value= '<my test>'

        # Save first.
        secret = secrets.Get(name)
        secret.SetValue(value)

        # Read the value and compare
        read = secret.GetValue()
        TESTS.AssertEqual(value, read)

        # Update.
        value= '<my test updated>'
        secret.SetValue(value)

        # Read the value and compare
        read = secret.GetValue()
        TESTS.AssertEqual(value, read)

        # Delete and read again.
        secret.Delete()
        with TESTS.AssertValidation():
            read = secret.GetValue()
