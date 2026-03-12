from NLWEB import NLWEB
from SESSION import SESSION
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_ENTITY_PROPERTY_EXTERNAL(STRUCT):
    '''
    External  # Loads ONE|MANY options from an external domain.
        - From  # Domain providing the information.
        - Read  # Code structure to read from the source.
        - Show  # Returned property to show to the user.
        - Save  # Returned property to be saved.
    '''


    def Verify(self):
        self.Require()
        self.RequireFrom()
        self.RequireRead()
        self.RequireShow()
        self.RequireSave()


    def RequireFrom(self):
        return self.RequireStr('From')


    def RequireRead(self):
        return self.RequireStr('Read')


    def RequireShow(self):
        return self.RequireStr('Show')

    
    def RequireSave(self):
        ''' 👉 Returns a list of properties to save.'''
        save = self.RequireAtt('Save')
        if UTILS.IsType(save, str):
            return [save]
        return self.ListStr('Save', require=True)
    

    def GetRemoteOptions(self, language:str):
        ''' 👉 Gets the list of options from a remote domain.'''

        # Get the session's language.
        language = language[:2]

        # Get the remote dataset.
        dataset = NLWEB.ROLES().DATASET().InvokeQuery(
            supplier= self.RequireFrom(),
            output= self.RequireRead(),
            input= {'Language': language})
        
        # Build the list from the dataset.
        options = []
        displayProp = self.RequireShow()
        for item in dataset:
            displayValue = item.RequireStr(displayProp)
            options.append(displayValue)

        return options