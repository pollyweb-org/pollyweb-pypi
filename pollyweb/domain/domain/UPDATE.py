# 📚 UPDATE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations
from pollyweb import LOG

from pollyweb import STRUCT
from MSG import MSG
from pollyweb import UTILS


class UPDATE(STRUCT):
    ''' 👉 Update to a domain.

    Example:
    {
        'ID': <domain>/<correlation>
        'UpdateID': domain.UpdateID(),
        'Domain': 'any-domain.com',
        'SentAt': domain.Timestamp(),
        'Correlation: <uuid>
    }
    '''

    def Verify(self):
        '''👉 Verifies if the required fields are present.'''

        self.RequireUpdateID()
        self.RequireDomain()
        self.RequireSentAt()
        self.RequireCorrelation()

        if self.ContainsAtt('ItemVersion'):
            LOG.RaiseValidationException('ItemVersion should not be exposed!')


    def RequireUpdateID(self):
        # Rename ID for UpdateID, if necessary.
        if self.IsMissingOrEmpty('UpdateID'):
            if not self.IsMissingOrEmpty('ID'):
                self['UpdateID'] = self.RequireStr('ID')
                self.RemoveAtt('ID')
                self.MoveAtt('UpdateID', new_position=0)
        # Return normally.
        return self.RequireUUID('UpdateID')
    

    def RequireDomain(self):
        return self.RequireStr('Domain')
    
    
    def RequireCorrelation(self):
        return self.RequireUUID('Correlation')
    

    def RequireSentAt(self):
        return self.RequireTimestamp('SentAt')


    @staticmethod
    def FromMsg(msg:MSG) -> UPDATE:
        '''👉 Creates an UPDATE from a MESSAGE'''
        
        ##LOG.Print(f"UPDATE()")
        ##LOG.Print(" " + str(msg))

        update = UPDATE({
            'UpdateID': msg.GetAtt(
                name= 'UpdateID', 
                default= msg.RequireCorrelation()
            ), 
            'SentAt': msg.RequireTimestamp(
                att= 'SentAt', 
                default= msg.GetTimestamp()
            ),
            'Domain': msg.GetAtt(
                name= 'Domain', 
                default= msg.RequireFrom()
            ),
            'Correlation': msg.GetAtt(
                name= 'Correlation', 
                default= msg.RequireCorrelation()
            )
        })
        return update
    

    @staticmethod
    def New(updateID:str, domain:str, timestamp:str, correlation:str) -> UPDATE:
        ''' 👉 Instanciates a new UPDATE in memory.'''
        
        UTILS.RequireArgs([updateID, domain, timestamp, correlation])

        item = {
            'Domain': domain,
            'UpdateID': updateID,
            'SentAt': timestamp,
            'Correlation': correlation
        }

        return UPDATE(item)
