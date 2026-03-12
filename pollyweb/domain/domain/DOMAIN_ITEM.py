# 🪣 BUYER_SUPPLIER

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union
from PW_AWS.DYNAMO_BASE import DYNAMO_BASE
from pollyweb import LOG
from MSG import MSG
from PW_AWS.ITEM import ITEM
from pollyweb import UTILS


# ✅ DONE
class DOMAIN_ITEM(ITEM):
    '''🪣 List of related domains
    Example:
        ID: any-customer.com
        IsActive: True
    '''


    @classmethod
    def _Table(cls) -> DYNAMO_BASE:
        LOG.RaiseException('Domain items must be overriden to contextualize them!')
    

    @classmethod
    def RequireDomain(cls, domain:Union[str,MSG]):

        UTILS.Require(domain)
        UTILS.AssertIsAnyType(domain, [str,MSG])

        if isinstance(domain, MSG):
            domain.Require()
            domain = domain.RequireFrom()

        item = cls._Table().Require(domain)

        return cls(item)


    @classmethod
    def Insert(cls, domain:str):
        item = {
            'ID': domain,
            'IsActive': True
        }
        cls._Table().Insert(item)


    def IsActive(self)-> bool:
        return self.RequireBool('IsActive')

    def Codes(self)-> list[str]:
        self.RequireAtt('Codes')
        return self.ListStr('Codes')

    def Domain(self)-> str:
        return self.RequireStr('ID')


    def VerifyIsActive(self):
        self.RequireID()
        self.Match('IsActive', True)


    @classmethod
    def ActiveOnes(cls) -> list[str]:
        '''👉 Returns only the active items.'''
        ret:list[str] = []

        for item in cls._Table().GetAll():
            supplier = cls(item)
            
            if supplier.IsActive():
                ret.append(supplier.RequireID())

        UTILS.Require(ret, 
            msg=f'No active domains found on cls=({type(cls).__name__})!')
        
        return ret