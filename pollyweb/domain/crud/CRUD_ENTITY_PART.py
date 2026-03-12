from pollyweb import STRUCT


class CRUD_ENTITY_PART(STRUCT):
    '''👉 Helper for dictionary-indexed parts.'''

    def __init__(self, obj:dict, entity, name:str):
        '''👉 Helper for dictionary-indexed parts.
            - object: the entity part item.
            - entity: parent entity.
            - name: name of the part as index in the dictinary.
        '''

        super().__init__(obj)
        
        # Map the parent entity.
        from CRUD_ENTITY import CRUD_ENTITY
        CRUD_ENTITY.AssertClass(entity, require=True)
        self._entity = entity

        # Get the name from the dicionary.
        self.RequireAtt('Name', set=name)


    def RequireEntity(self):
        '''👉 Returns a reference to the parent entity.'''
        from CRUD_ENTITY import CRUD_ENTITY
        ret:CRUD_ENTITY = self._entity
        return ret
    

    def RequireName(self):
        '''👉 Returns the name (i.e., the dictionary index).'''
        return self.RequireStr('Name')


    @classmethod
    def CastToList(cls, entity, dictionary:dict):
        '''👉 Casts a generict dictionary into a list of entity parts.'''

        # Verify the entity.
        from CRUD_ENTITY import CRUD_ENTITY
        CRUD_ENTITY.AssertClass(entity, require=True)

        # Get the internal dictionary from a STRUCT.
        if isinstance(dictionary, STRUCT):
            dictionary = dictionary.Obj()

        # Cast the list.
        ret:list[cls] = []
        for name in dictionary:
            obj = dictionary[name]
            prop = cls(obj, entity=entity, name=name)
            ret.append(prop)

        # Return the list.
        return ret
