from PW_AWS.AWS_TEST import AWS_TEST
from DATASET import DATASET


class DATASET_MOCKS(DATASET, AWS_TEST):

    @classmethod
    def MockDataset(cls, domain:str):
        
        cls.MOCKS().SYNCAPI().MockHandler(
            domain= domain, 
            subject= 'Query@Dataset',
            handler= cls.HandleQuery,
            ignoreValidation= False)