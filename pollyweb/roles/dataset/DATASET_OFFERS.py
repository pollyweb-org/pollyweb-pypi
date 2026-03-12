
from PW_AWS.AWS import AWS
from DATASET_OFFER import DATASET_OFFER


class DATASET_OFFERS:

    
    @classmethod
    def _Table(cls):
        return AWS.DYNAMO('DATASETS')
    

    @classmethod
    def RequireOffer(cls, code:str):
        item = cls._Table().Require(code)
        ret = DATASET_OFFER(item)
        ret.Verify()
        return ret


    @classmethod
    def Insert(cls, code:str, location:str):
        item = {
            'ID': code,
            'Location': location
        }

        DATASET_OFFER(item).Verify()

        cls._Table().Insert(item)