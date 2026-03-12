from CRUD_ENTITY import CRUD_ENTITY
from CRUD_WALLET_ENTITY import CRUD_WALLET_ENTITY
from NLWEB import NLWEB
from PW_AWS.ITEM import ITEM
from pollyweb import LOG


class CRUD_WALLET(ITEM):
    '''
        ID: <uuid>
        PublicKey: <publicKey>
        Binds: 
          - ID: 429e0b51-4a30-43bd-9d20-5648ec1c5350
            Code: pollyweb.org/VAULT/BIND
    '''
    

    @classmethod
    def ENTITIES(cls):
        return NLWEB.BEHAVIORS().CRUD().ENTITIES()
    
    @classmethod
    def ITEMS(cls):
        return NLWEB.BEHAVIORS().CRUD().WALLETS().ITEMS()


    def RequireEntities(self):
        self.Default('Entities', {})
        return self.GetStruct('Entities')
    

    def RequireEntityByName(self, name:str):
        entity = NLWEB.BEHAVIORS().CRUD().RequireEntity(name)
        return self.RequireEntity(entity)


    def RequireEntity(self, entity:CRUD_ENTITY):
        LOG.Print('😃 CRUD.WALLET.RequireEntity()', entity)
        CRUD_ENTITY.AssertClass(entity, require=True)
        
        name = entity.RequireName()
        
        entities = self.RequireEntities()
        entities.Default(name, {})
        ret = entities.RequireStruct(name)

        return CRUD_WALLET_ENTITY(ret, 
            wallet= self, 
            entity= entity)
    
