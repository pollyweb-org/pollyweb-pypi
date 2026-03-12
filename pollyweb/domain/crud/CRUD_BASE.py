
from pollyweb import UTILS


class CRUD_BASE():
    

    @classmethod
    def ENTITIES(cls):
        from CRUD_ENTITIES import CRUD_ENTITIES
        return CRUD_ENTITIES()

    @classmethod
    def MODELS(cls):
        from CRUD_MODEL import CRUD_MODEL
        return CRUD_MODEL()

    @classmethod
    def WALLETS(cls):
        from CRUD_WALLETS import CRUD_WALLETS
        return CRUD_WALLETS()


    @classmethod
    def RequireEntity(cls, entityName:str):
        UTILS.Require(entityName)
        
        ''' 👉 Returns an entity configuration.'''
        return cls.ENTITIES().RequireEntity(
            modelName= 'wallet',
            entityName= entityName)
        
