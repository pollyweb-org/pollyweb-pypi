

from NLWEB import NLWEB
from pollyweb import STRUCT


class CRUD_MODEL_GROUP(STRUCT):
    '''
    - Title: Wellbeing
    - Folder: /wallet/Wellbeing
    - Entities: [Meals, Allergy, Emergency]
    '''
    

    def Verify(self):
        '''👉 Verifies if the required properties are set.'''
        
        self.RequireTitle()
        self.RequireFolder()
        self.RequireEntities()


    def RequireTitle(self):
        '''👉 Returns the group's name.'''
        return self.RequireStr('Title')
    
    def RequireFolder(self):
        '''👉 Returns the group's folder.'''
        return self.RequireStr('Folder')
    
    def RequireEntities(self):
        '''👉 Returns the list of entity names.'''
        return self.RequireStruct('Entities')
    

    def _LoadEntitiesFromDir(self, root:str):
        '''👉 Load all entities to memory.'''
        folder = self.RequireFolder()
        
        from CRUD_ENTITY import CRUD_ENTITY
        ret:dict[str,CRUD_ENTITY] = {}

        for name in self.ListStr('Entities'):
            path = f'{root}{folder}/🪣 {name}.yaml'
            entity = NLWEB.BEHAVIORS().CRUD().ENTITIES().LoadEntityFromFile(path)
            ret[name] = entity
        return ret

