from __future__ import annotations
from pollyweb import LOG

from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_ENTITY(STRUCT):
    '''
    Structure:
      - About # Singleton configuration of the entitity.
      - Properties # List of properties in the entity.
      - Exports # List of codes exported by the entity.
    '''


    def __init__(self, obj:any, name:str):
        super().__init__(obj)
        self._name = name


    def RequireName(self):
        return self._name


    def Verify(self):
        self.Require()
        self.RequireAbout().Verify()
        for prop in self.RequireProperties():
            prop.Verify()


    def RequireAbout(self):
        '''👉 Returns the about section.'''
        about = self.RequireStruct('About')
        from CRUD_ENTITY_ABOUT import CRUD_ENTITY_ABOUT
        return CRUD_ENTITY_ABOUT(about, self)


    def RequireProperties(self):
        '''👉 Returns the list of properties.'''
        props = self.RequireStruct('Properties')
        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        return CRUD_ENTITY_PROPERTY.CastToList(self, props)


    def RequireProperty(self, name:str):
        '''👉 Returns a specific property.'''
        if name == None: return None
        for prop in self.RequireProperties():
            if prop.RequireName() == name: return prop
        LOG.RaiseException(f'Property not found: {name}', self)


    def RequireHumanPropertyList(self):
        '''👉 Returns a human-readable list of properties:
        - Props=[A] -> A
        - Props=[A,B] -> A, and B
        - Props=[A,B,C] -> A, B, and C
        '''
        LOG.Print('😃 CRUD.ENTITY.RequireHumanPropertyList()')

        props = self.RequireProperties()

        ttls = STRUCT({})
        for p in props:
            name = p.RequireName()
            title = p.RequireTitle()
            ttls.SetAtt(name, title)

        # Fill groups with property titles.
        # { None:['a','b'], b:['c','d'], d:['e','f'] }
        grps = STRUCT({})
        for p in props:
            if p.GetIf() == None: name = 'NONE'
            else: name = p.GetIf().RequireName()

            title = p.RequireTitle()
            if p.RequireFormat() == 'CONFIRM':
                title = f'{title} confirmation'

            grps.AppendToAtt(name, [title])

        LOG.Print('😃 CRUD.ENTITY.RequireHumanPropertyList.grps:', grps)

        # Transform groups into strings.
        # { None:'a&b', b:'c&d', d:'e&f' }
        for g in grps.Attributes():
            titles = grps[g]
            if len(titles) > 1:
                titles[-1] = 'and ' + titles[-1]
            grps[g] = ', '.join(titles)

        # Compose the final lines.
        for g in grps.Attributes():
            title = ttls[g]
            props = grps[g]
            if g == 'NONE':
                grps[g] = f"Next, I'll ask you for: {props}."
            else:
                grps[g] = \
                    f"- If you confirm {title}, " + \
                    f"then I'll ask you for: {props}."
    
        # Merge the lines.
        lines = []
        for g in grps.Attributes():
            lines.append(grps[g])

        # Return a multi-line string.
        ret = '\n'.join(lines)

        LOG.Print('😃 CRUD.ENTITY.RequireHumanPropertyList.ret:', ret)

        return ret


    def RequireExports(self):
        '''👉 Returns the list of exports.'''
        exports = self.RequireStruct('exports')
        from CRUD_ENTITY_EXPORT import CRUD_ENTITY_EXPORT
        return CRUD_ENTITY_EXPORT.CastToList(self, exports)


    def RequireExport(self, name:str):
        '''👉 Returns a specific export.'''
        if name == None: return None
        for export in self.RequireExports():
            if export.RequireName() == name: return export
        LOG.RaiseException(f'Export not found: {name}', self)


    def CalculateNextIndex(self, index:int, item:dict=None, stage:dict=None):
        '''👉 Calculates the next property index.'''

        entity = self
        props = entity.RequireProperties()
        maxIndex = len(props)-1

        # Check if the next ones are visible OTP.
        visible = False
        while not visible:

            if index > maxIndex: 
                return -1

            if index < maxIndex: 
                
                # Look at the next property.
                prop = props[index+1]
                
                # Hide OTP on updates that don't change the dependent properties.
                if self._HideOTP(prop=prop, item=item, stage=stage): pass 
                # Hide properties dependent on CONFIRMs answered NO.
                elif self._HideIf(prop=prop, stage=stage): pass
                # Otherwise, show the property.
                else: visible = True                

            index = index+1

        # Return -1 if there are no more properties.
        if index > maxIndex: 
            return -1
        return index
    

    def _HideIf(self, prop:STRUCT, stage:dict):
        '''👉 Hide properties dependent on CONFIRMs answered NO.'''

        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        prop:CRUD_ENTITY_PROPERTY = prop

        dependency = prop.GetIf()
        if UTILS.IsNoneOrEmpty(dependency):
            return False
        
        if dependency.RequireFormat() != 'CONFIRM':
            return False
        
        name = dependency.RequireName()
        if stage[name] == 'YES':
            return False
        
        # It's pendent on a CONFIRM answered NO.
        return True


    def _HideOTP(self, prop:STRUCT, item:dict, stage:dict):
        '''👉 Hide OTP on updates that don't change the dependent properties.'''

        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        prop:CRUD_ENTITY_PROPERTY = prop

        # See if it's an update.
        if item == None or stage == None:
            return False 
        
        # See if it's an OTP.
        if prop.RequireFormat() != 'OTP':
            return False
        
        # See if the dependent fields were changed.
        for sendProp in prop.RequireSend():
            name = sendProp.RequireName()
            if item[name] != stage[name]:
                return False

        # It's OTP on an update, but nothing changed.
        return True