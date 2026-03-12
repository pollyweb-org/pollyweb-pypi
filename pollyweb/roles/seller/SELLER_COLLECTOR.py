from DOMAIN_ITEM import DOMAIN_ITEM
from PW_AWS.AWS import AWS


class SELLER_COLLECTOR(DOMAIN_ITEM):
    
    @classmethod
    def _Table(cls):
        return AWS.DYNAMO('COLLECTORS')