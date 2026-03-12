from __future__ import annotations

from PW_AWS.ITEM import ITEM
from pollyweb import LOG
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_WALLET_ITEM(ITEM):

    
    def __init__(self, item:any, walletEntity):
        
        from CRUD_WALLET_ENTITY import CRUD_WALLET_ENTITY
        CRUD_WALLET_ENTITY.AssertClass(walletEntity, require= True)
        
        super().__init__(item)
        self._walletEntity = walletEntity


    def RequireWalletEntity(self):
        '''👉 Returns the base entity.'''
        from CRUD_WALLET_ENTITY import CRUD_WALLET_ENTITY
        ret:CRUD_WALLET_ENTITY = self._walletEntity
        return ret
    

    def RequireEntity(self):
        '''👉 Returns the base entity.'''
        from CRUD_WALLET_ENTITY import CRUD_WALLET_ENTITY
        entity:CRUD_WALLET_ENTITY = self.RequireWalletEntity()
        return entity.RequireEntity()
    

    def RequireProperties(self):
        '''👉 Returns the base entity's properties.'''
        return self.RequireEntity().RequireProperties()


    def GetViewMessage(self):
        '''👉 Returns a human readable list of item values.'''

        entity = self.RequireEntity()

        one = entity.RequireAbout().RequireOne()
        props = entity.RequireProperties()
        lines = []
        for prop in props:
            if prop.RequireFormat() != 'OTP':
                title = prop.RequireTitle()
                value = self.GetAtt(prop.RequireName())
                line = f'- {title}: {value}'
                lines.append(line)
        lines = '\n'.join(lines)

        about = entity.RequireAbout()
        format = about.RequireFormat()

        if format == 'ONE':
            ret = f"Here are the details:"

        elif format == 'MANY':
            one = about.RequireOne().lower()
            ret = f"Here are the **{one}** details:"

        else:
            LOG.RaiseException('Unexpected format!', format)

        ret = ret + f'\n{lines}'
        return ret
    

    def CalculateViewMessage(self):
        # Build the message.
        message = self.GetViewMessage() + \
            "\n😌 Anything else?"
        return message


    def CalculateViewOptions(self):

        # Get the context.
        entity = self.RequireEntity()
        walletEntity = self.RequireWalletEntity()
        
        # Build the options for instance.
        one = entity.RequireAbout().RequireOne()
        options = {}
        options['UPDATE'] = f'Update {one.lower()}'
        
        if entity.RequireAbout().RequireFormat() != 'ONE':
            options['DELETE'] = f'Delete {one.lower()}'
        
        if walletEntity.Count() > 1:
            options['ANOTHER'] = 'View another'
    
        return options


    @classmethod
    def Verify(cls, item:dict):
        struct = STRUCT(item)
        struct.Require()

        # Revove the TTL that came from staging.
        if struct.ContainsAtt('TTL'):
            struct.RemoveAtt('TTL')

        # Verify all.
        atts = struct.Attributes()
        if UTILS.ContainsAny(atts, ['TTL']):
            LOG.RaiseException('Invalid attribute in item.')
