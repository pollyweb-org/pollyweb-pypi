from __future__ import annotations
from CRUD_ENTITY import CRUD_ENTITY
from PW_AWS.AWS import AWS
from pollyweb import UTILS


class CRUD_ENTITIES:
    
    @classmethod
    def _Table(cls):
        return AWS.DYNAMO('ENTITIES')


    @classmethod
    def RequireEntity(cls, modelName:str, entityName:str):
        
        # Verify args
        UTILS.RequireArgs([modelName, entityName])

        id = f'{modelName}/{entityName}'
        item = cls._Table().Require(id)
        return CRUD_ENTITY(item, name=entityName)


    @classmethod
    def Insert(cls, modelName:str, entityName:str, entity:CRUD_ENTITY):

        # Verify args
        CRUD_ENTITY.AssertClass(entity, require=True)
        UTILS.AssertIsType(modelName, str, require=True)

        entity:CRUD_ENTITY = entity
        entity['ID'] = f'{modelName}/{entityName}'

        entity.Verify()
        cls._Table().Insert(entity)
        
        return entity


    @classmethod
    def LoadEntityFromFile(cls, path:str):
        '''👉️ Loads the entity from a yaml file.'''
        
        # Read the file.
        file = UTILS.OS().File(path)
        obj = file.ReadYaml()
        
        # cast the entity.
        entity = CRUD_ENTITY(obj, 
            name= file.GetNameWithoutExtension())
        entity.Verify()

        # Return the entity.
        return entity
    