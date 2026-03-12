
from PW_AWS.AWS_TEST import AWS_TEST
from TRANSFER import TRANSFER


class TRANSFER_MOCKS(TRANSFER, AWS_TEST):
    
    @classmethod
    def MockTransfer(cls, domain):
        cls.MOCKS().SYNCAPI().MockHandler(
            domain= domain, 
            subject= 'Download@Transfer',
            ignoreValidation= False,
            handler= cls.HandleDownload)