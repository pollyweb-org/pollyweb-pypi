from CRUD_WALLET import CRUD_WALLET
from NLWEB import NLWEB
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_ENTITY_PROPERTY_INTERNAL(STRUCT):
    '''
    Loads ONE|MANY options from an internal entity.
        - From  # Entity providing the information.
        - Show  # Returned property to show to the user.
        - Save  # Returned property to be saved.
    '''

    def __init__(self, obj:any, property):
        super().__init__(obj)

        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        CRUD_ENTITY_PROPERTY.AssertClass(property, require=True)
        self._property = property


    def RequireProperty(self):
        '''👉 Returns a reference to the parent property.'''
        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        ret:CRUD_ENTITY_PROPERTY = self._property
        return ret
    

    def RequireEntity(self):
        '''👉 Returns a reference to the entity of the parent property.'''
        return self.RequireProperty().RequireEntity()


    @classmethod
    def ENTITIES(cls):
        from CRUD_ENTITIES import CRUD_ENTITIES
        return CRUD_ENTITIES()


    def Verify(self):
        self.Require()
        self.RequireFrom()
        self.RequireShow()
        self.RequireSave()


    def RequireFrom(self):
        return self.RequireStr('From')


    def RequireShow(self):
        return self.RequireStr('Show')

    
    def RequireSave(self):
        ''' 👉 Returns a list of properties to save.'''
        save = self.RequireAtt('Save')
        if UTILS.IsType(save, str):
            return [save]
        return self.ListStr('Save', require=True)
    

    def GetInternalOptions(self, wallet:CRUD_WALLET):
        ''' 👉 Gets the list of options from an internal dataset.'''

        # Get the internal dataset.
        fromName = self.RequireFrom()
        walletEntity = wallet.RequireEntityByName(fromName)
        dataset = walletEntity.GetAllItems()
        
        # Build the list from the dataset.
        options = []
        displayProp = self.RequireShow()
        for item in dataset:
            displayValue = item.RequireStr(displayProp)
            options.append(displayValue)

        return options