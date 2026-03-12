# 📚 SELLER

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations
from typing import Union

from pollyweb import LOG

from PW_AWS.ITEM import ITEM
from pollyweb import UTILS
from CHARGE import CHARGE
from PW_AWS.AWS import AWS

from SELLER_COLLECTOR import SELLER_COLLECTOR

   

# ✅ DONE
class SELLER_CHARGE(ITEM):
    '''👉 List of charges with amounts.

    Example:
    {
        "ID": ...,
        "Amount": 0.00,
        "Currency": currency,
        "Operation": 'DEBIT',
        "ChargedOn": <timestamp>,
        "Collectors": ["any-collector.org"],
        "Paid": False,
        "PaidOn": <timestamp>,
        "Collector": "any-collector.org",
        "Transaction": {...}
    }
    '''


    @staticmethod
    def Insert(amount:float, currency:str, collectors:list[str]) -> SELLER_CHARGE:

        UTILS.RequireArgs([amount, currency, collectors])
        UTILS.AssertIsType(amount, float)
        UTILS.AssertIsType(collectors, list)
        UTILS.AssertIsType(currency, str)
        
        item = SELLER_CHARGE({
            "ID": UTILS.UUID(),
            "Amount": amount,
            "Currency": currency,
            "Operation": 'DEBIT',
            "ChargedOn": UTILS.GetTimestamp(),
            "Collectors": collectors,
            "Paid": False,
            "PaidOn": None,
            "Collector": None
        })

        item.VerifyCharge()
        SELLER_CHARGE._table().Insert(item)

        UTILS.AssertIsType(item, SELLER_CHARGE)
        return item
    

    def ToCharge(self):
        ret = CHARGE.New(
            chargeID= self.RequireID(),
            amount= self.RequireAmount(),
            currency= self.RequireCurrency(),
            operation= self.RequireOperation(),
            collectors= self.RequireCollectors()
        )
        ret.VerifyCharge()
        return ret


    @staticmethod
    def _table():
        return AWS.DYNAMO('CHARGES')
    

    @staticmethod
    def RequireCharge(charge:Union[str,CHARGE]) -> SELLER_CHARGE:
        UTILS.AssertIsAnyType(charge, [str,CHARGE])

        if isinstance(charge, CHARGE):
            chargeID = charge.RequireChargeID()
        else:
            chargeID = charge

        item = SELLER_CHARGE._table().Require(chargeID)
        return SELLER_CHARGE(item)
    

    def RequireCollectors(self) -> list[str]:
        collectors = self.ListStr('Collectors', require=True)
        if len(collectors) == 0:
            LOG.RaiseException('Register at least one Collector first.')
        return collectors


    def RequireAmount(self) -> float:
        return self.RequireFloat('Amount')
    

    def RequireCurrency(self) -> str:
        return self.RequireStr('Currency')
    

    def RequireOperation(self) -> str:
        return self.RequireStr('Operation')
    

    def MatchCharge(self, charge:Union[CHARGE,SELLER_CHARGE]):
        '''👉 Verifies if the amount and operation match.'''

        UTILS.AssertIsAnyType(charge, [CHARGE, SELLER_CHARGE])

        if isinstance(charge, SELLER_CHARGE):
            charge = charge.ToCharge()

        UTILS.AssertIsType(charge, CHARGE)
        
        self.Match('Amount', charge.RequireAmount())
        self.Match('Currency', charge.RequireCurrency())
        self.Match('Operation', charge.RequireOperation())


    def RequiredPaid(self, set:bool=None):
        return self.RequireBool('Paid', set=set)


    def Pay(self, collector:SELLER_COLLECTOR, transaction:any):
        self.VerifyNotPaid()
        self.RequiredPaid(set=True)

        # Update the info.
        self.Merge({
            'Collector': collector.Domain(),
            'PaidOn': UTILS.GetTimestamp(),
            'Transaction': transaction
        })
        
        self.UpdateItem()


    def VerifyNotPaid(self):
        # Check if it was already paid.
        if self.RequiredPaid():
            LOG.RaiseException('Already paid!')
        

    def VerifyCharge(self):
        self.RequireAmount()
        self.RequireCurrency()
        self.RequireOperation()
        self.RequireCollectors()
        self.RequireCollectors()
        self.RequiredPaid()
