
from CRUD_ENTITY_PART import CRUD_ENTITY_PART
from CRUD_WALLET import CRUD_WALLET
from pollyweb import UTILS


class CRUD_ENTITY_PROPERTY(CRUD_ENTITY_PART):
    '''
    Property in an entity.
        - Default   # Default value for the user prompt.
        - Details   # Additional user prompt message.
        - External  # Loads ONE|MANY options from an external domain.
        - Format    # Prompt format for the wallet user, e.g. TEXT.
        - If        # Show this property if another is True.
        - Internal  # Loads ONE|MANY options from an internal entity.
        - MaxLength # Maximum lenght for TEXT|EMAIL formats.
        - MinLength # Minimum lenght for TEXT|EMAIL formats.
        - Options   # Lodas ONE|MANY options with static values.
        - Send      # Array of properties to send to a Supplier.
        - Title     # Display override for the name of the property.
        - Unique    # Is there a unique index in the property? 
    '''


    def Verify(self):
        self.RequireName()
        self.RequireDetails()
        self.RequireFormat()


    def GetDefault(self):
        '''👉 Default value for the user prompt.
              - For [CONFIRM], highlights the YES or NO button.
              - For [ONE,MANY], moves the option to the top.
              - For [TEXT], pre-types the text.'''
        return self.GetStr('Default')
    
    
    def RequireDetails(self):
        '''👉 Additional user prompt message.
              - Tipically, a description of the field.'''
        return self.RequireStr('Details')


    def GetExternal(self):
        '''👉 Loads ONE|MANY options from an external domain.'''
        external = self.GetStruct('External')
        if external.IsMissingOrEmpty():
            return None
        
        from CRUD_ENTITY_PROPERTY_EXTERNAL import CRUD_ENTITY_PROPERTY_EXTERNAL
        external = CRUD_ENTITY_PROPERTY_EXTERNAL(external)
        external.Verify()
        return external


    def RequireFormat(self):
        '''👉 See details in https://quip.com/CDrjAxNKwLpI
              - If [ONE,MANY] requires Options or Lookup.
              - If [OTP] requires Data.
              - Defaults to TEXT.
        '''
        return self.RequireStr('Format', default='TEXT')


    def GetIf(self):
        '''👉 Show this property if another is True.
              - The conditional property must have format CONFIRM.'''
        ifProperty = self.GetStr('If')
        return self.RequireEntity().RequireProperty(ifProperty)


    def GetInternal(self):
        '''👉 Loads ONE|MANY options from an internal entity.
            - The entity should remain unavailable until there is at least one
                item in the table of the dependent entities.'''
        internal = self.GetStruct('Internal')
        if UTILS.IsNoneOrEmpty(internal):
            return None

        from CRUD_ENTITY_PROPERTY_INTERNAL import CRUD_ENTITY_PROPERTY_INTERNAL
        internal = CRUD_ENTITY_PROPERTY_INTERNAL(internal, property=self)
        internal.Verify()
        return internal


    def GetMaxLength(self):
        '''👉 Maximum lenght for TEXT|EMAIL formats.'''
        return self.GetInt('MaxLength')


    def GetMinLength(self):
        '''👉 Minimum lenght for TEXT|EMAIL formats.'''
        return self.GetInt('MinLength')


    def RequireOptions(self):
        '''👉 List of options'''
        options = self.RequireAtt('Options')
        UTILS.AssertIsAnyType(options, [list,dict])
        return options


    def GetOptions(self):
        '''👉 List of options'''
        options = self.GetAtt('Options')
        UTILS.AssertIsAnyType(options, [list,dict])
        return options
    

    def RequireSend(self):
        '''👉 Array of properties to send to a Supplier.'''
        names = self.ListStr('Send', require=True)
        props:list[CRUD_ENTITY_PROPERTY] = []
        for name in names:
            prop = self.RequireEntity().RequireProperty(name)
            props.append(prop)
        return props


    def RequireTitle(self):
        '''👉 Display override for the name of the property.
            - If there is no title, the property name is used.
            - Used for single-word properties that need titles with 2+ words.'''
        name = self.RequireName()
        return self.GetStr('Title', default=name)


    def RequireUnique(self):
        '''👉 Is there a unique index in the property? 
            - This will be validated after each input.
            - The workflow remains blocked while not unique.'''
        return self.RequireBool('Unique', default=False)
    

    def CalculateOptions(self, language:str, wallet:CRUD_WALLET):
        '''👉 Build the options.'''

        external = self.GetExternal()
        if external != None:
            return external.GetRemoteOptions(language)

        internal = self.GetInternal()        
        if internal != None:
            return internal.GetInternalOptions(wallet)
        
        return self.GetOptions()