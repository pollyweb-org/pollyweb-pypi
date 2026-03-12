from CRUD_WALLET_ENTITY import CRUD_WALLET_ENTITY
from CRUD_WALLET_ITEM import CRUD_WALLET_ITEM
from PW_AWS.AWS import AWS
from pollyweb import UTILS


class CRUD_WALLET_ITEMS:


    @classmethod
    def _Table(cls): 
        return AWS.DYNAMO('WALLET_ITEMS')
    

    @classmethod
    def RequireItem(cls, id:str, walletEntity:CRUD_WALLET_ENTITY):
        UTILS.Require(id, msg= 'ItemID not provided!')
        CRUD_WALLET_ENTITY.AssertClass(walletEntity, require=True)
        item = cls._Table().Require(id)
        return CRUD_WALLET_ITEM(item, walletEntity)
    

    @classmethod
    def InsertItem(cls, item:dict):
        CRUD_WALLET_ITEM.Verify(item)
        return cls._Table().Insert(item)

