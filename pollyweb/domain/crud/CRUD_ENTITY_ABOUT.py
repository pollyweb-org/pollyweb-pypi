

from pollyweb import LOG
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_ENTITY_ABOUT (STRUCT):
    '''
    Singleton configuration of the entitity.
        - Details  # Detailed information about the entity.
        - Format   # Indicates the multiplicity, ex. [ONE,MANY]
        - List     # Property to be presented in lists.
        - Many     # Name for multiple entities, ex. Feet.
        - One      # Name for one single entity, ex. Foot.
    '''


    def RequireDetails(self):
        '''👉 Detailed information about the entity.'''
        return self.RequireStr('Details')
    
    
    def RequireFormat(self):
        '''👉 Indicates the multiplicity, ex. [ONE,MANY]'''
        ret = self.RequireStr('Format')
        UTILS.AssertIsAnyValue(ret, ['ONE', 'MANY'])
        return ret
    
    
    def RequireList(self):
        '''👉 Property to be presented in lists.
        * It must have a unique index.'''
        return self.RequireStr('List')
    

    def GetList(self):
        '''👉 Property to be presented in lists.
        * It must have a unique index.'''
        return self.GetStr('List')
    

    def GetRank(self):
        '''👉 Property to order lists.'''
        return self.GetStr('Rank')
    

    def RequireMany(self):
        '''👉 Name for multiple entities, ex. Feet.'''

        if self.RequireFormat() == 'ONE':
            if self.GetStr('Many') != None:
                LOG.RaiseException(
                    'Invalid operation!', 
                    'Dont ask for a plural name when Format equals ONE.')
            return None
            
        return self.RequireStr('Many')
    

    def RequireOne(self):
        '''👉 Name for one single entity, ex. Foot.'''
        return self.RequireStr('One')


    def Verify(self):
        self.Require()
        self.RequireDetails()
        self.RequireFormat()
        self.RequireOne()
        self.RequireMany()
        self.GetList()
        self.GetRank()