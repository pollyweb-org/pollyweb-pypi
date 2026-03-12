from NLWEB import NLWEB
from PW_AWS.AWS import AWS
from pollyweb import LOG
from pollyweb import STRUCT
from pollyweb import UTILS
from pollyweb import DIRECTORY


class CRUD_MODEL(STRUCT):


    @classmethod
    def _Table(cls):
        return AWS.DYNAMO('MODELS')
    

    @classmethod
    def RequireModel(cls, name:str):
        item = cls._Table().Require(name)
        return CRUD_MODEL(item)


    @classmethod
    def _Insert(cls, model, name:str):
        CRUD_MODEL.AssertClass(model, require=True)
        model:CRUD_MODEL = model
        
        model['ID'] = name
        model.Verify()
        cls._Table().Insert(model)
        

    def Verify(self):
        '''👉 Verifies the required properties.'''
        groups = self.RequireGroups()
        for group in groups:
            group.Verify()


    def RequireGroups(self):
        '''👉 Returns the list of model groups.'''
        groups = self.Structs('Groups')
        from CRUD_MODEL_GROUP import CRUD_MODEL_GROUP
        return CRUD_MODEL_GROUP.FromStructs(groups)
         

    @classmethod
    def _LoadModelFromDir(cls, root:str):
        '''👉️ Loads the model from a yaml file.'''
        
        path = f'{root}/model.yaml'

        # Read the file.
        file = UTILS.OS().File(path)
        obj = file.ReadYaml()
        
        # cast the model.
        model = CRUD_MODEL(obj)

        # Return the model.
        return model
    

    def RequireRoot(self, set:str=None):
        '''👉 Gets or sets the location of the model.'''
        return self.RequireStr('Root', set=set)



    @classmethod
    def LoadDatabase(cls, dir:DIRECTORY):
        '''👉️ Loads the CRUD model from files, and saves it into the database.'''

        # Verify args.
        UTILS.AssertIsType(dir, DIRECTORY, require=True)

        # Parse the model from a file.
        model = cls._LoadModelFromDir(dir.GetPath())
        modelName = dir.GetName()
                
        # Parse the entities from files.
        for group in model.RequireGroups():
            entities = group._LoadEntitiesFromDir(dir.GetPath())
            LOG.Print(' CRUD.MODEL.LoadDatabase: entities=', entities)

            # Insert the entities  into a table.
            for entityName in entities:
                entity = entities[entityName]
                NLWEB.BEHAVIORS().CRUD().ENTITIES().Insert(
                    modelName= modelName,
                    entityName = entityName,
                    entity= entity)
                
            # Replace the list of entity names, for a dictionary of titles.
            entityTitles:dict[str,str] = {}

            for entityName in group.ListStr('Entities', require=True):
                entity = entities[entityName]
                about = entity.RequireAbout()
                if about.RequireFormat() == 'ONE':
                    title = about.RequireOne()
                else:
                    title = about.RequireMany()
                entityTitles[entityName] = title

            group.SetAtt('Entities', entityTitles) 
            
        # Insert the entity into a table.
        model.Verify()
        cls._Insert(model, name=modelName)