from CRUD_ENTITY_PART import CRUD_ENTITY_PART
from pollyweb import UTILS


class CRUD_ENTITY_EXPORT(CRUD_ENTITY_PART):
    '''
    List of codes exported by the entity.
        - Format  # Export only one item, or all items: ONE|MANY
        - If      # Export only if the given property is True.
        - Map     # Dictionary of properties to export in <name>:<value>.
        - Rank    # Name of rank property to sort the items.
    '''


    def Verify(self):
        self.RequireFormat()
        self.RequireMap()


    def RequireFormat(self):
        '''👉️ Export only one item, or all items.
        - If format is ONE and more that 1 item exists, then the user 
            will be asked to select the item on every share.
        '''
        ret = self.RequireStr('Format')
        UTILS.AssertIsAnyValue(ret, ['ONE', 'MANY'])
        return ret
    
    
    def GetIf(self):
        '''👉️ Export only if the given property is True.'''
        ifProp = self.GetStr('If')
        return self.RequireEntity().RequireProperty(ifProp)
    

    def RequireMap(self):
        '''👉️ Value or dictionary of properties to export in <name>:<value>.
            - The value can be a string or another dictionary.
            - Use '.' to reference sub properties, ex. 'Country.ISD'.
            - Use '@' to reference external entites, ex. 'Property@AnotherEntity'.
            - Properties of format MANY will are rendered as arrays.'''
        return self.RequireAtt('Map')
    

    def GetRank(self):
        '''👉️ Name of rank property to sort the items.
            - The property must have format RANK.
            - Order is descendent, from 5 starts to 1 star.'''
        rank = self.GetStr('Rank')
        return self.RequireEntity().RequireProperty(rank)