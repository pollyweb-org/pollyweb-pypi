# 🧾 CHARGE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from ..utils import STRUCT
from ..utils import UTILS
from ..utils import LOG

class CHARGE_OPTION(STRUCT):
    '''🧾
    Payer: any-payer.org
    Translation: AnyPayer
    BindID: <uuid>
    Collectors: [any-collector.org]
    '''

    def RequirePayer(self):
        return self.RequireStr('Payer')
    
    def RequireBindID(self):
        return self.RequireUUID('BindID')
    
    def RequireTranslation(self):
        return self.RequireStr('Translation')
    
    def RequireCollector(self):
        return self.RequireStr("Collector")

    def VerifyChargeOption(self):
        self.RequirePayer()
        self.RequireBindID()
        self.RequireTranslation()
        self.RequireCollector()


class CHARGE_OPTIONS(STRUCT):


    def RequireOptions(self):
        return [
            CHARGE_OPTION(x) 
            for x in self.GetList(mustExits=True)
        ]


    def VerifyChargeOptions(self):

        # Required arguments.
        for option in self.RequireOptions():
            option.VerifyChargeOption()

        # Unique payers.
        payers = [x.RequirePayer() for x in self.RequireOptions()]
        UTILS.VerifyDuplicates(payers)


    def RequireOption(self, payer:str):
        UTILS.Require(payer, msg='Payer is required in charge options.')
        lst = STRUCT(self.GetList())
        ret = lst.First('Payer', equals=payer, require=True)
        return CHARGE_OPTION(ret)
    
    
    def AddOption(self, payer:str, translation:str, collector:str, bindID:str):

        UTILS.RequireArgs([payer, translation, collector, bindID])
        UTILS.AssertIsUUID(bindID)

        option = CHARGE_OPTION({
            "Payer": payer,
            "Translation": translation,
            "Collector": collector,
            "BindID": bindID
        })

        option.VerifyChargeOption()
        
        self.Append(option)


class CHARGE(STRUCT):
    ''' 🧾 Charge from a seller.
    {
        "ChargeID": "61738d50-d507-42ff-ae87-48d8b9bb0e5a",
        "Amount": 12.34,
        "Currency": "USD",
        "Operation": "DEBIT",
        "Collectors": [ "any-collector.org" ]
    }
    '''


    @staticmethod
    def New(chargeID:str, amount:float, currency:str, operation:str, collectors:list[str]):
        
        LOG.Print(
            f'🧾 CHARGE.New()',
            f'{chargeID=}', f'{amount=}', f'{currency=}', f'{operation=}', f'{collectors=}')

        UTILS.RequireArgs([chargeID, amount, currency, operation, collectors])
        UTILS.AssertIsType(amount, float)

        return CHARGE({
            "ChargeID": chargeID,
            "Amount": amount,
            "Currency": currency,
            "Operation": operation,
            "Collectors": collectors
        })


    def Collectors(self) -> list[str]:
        return self.ListStr('Collectors', require=True)


    def RequireChargeID(self) -> str:
        return self.RequireUUID('ChargeID')
    

    def RequireAmount(self) -> float:
        return self.RequireFloat('Amount')
    
    
    def RequireAmountFormatted(self) -> str:
        amount = self.RequireAmount()
        return '{:,.2f}'.format(amount)
    

    def RequireCurrency(self) -> str:
        return self.RequireStr('Currency')
    

    def RequireOperation(self) -> str:
        return self.RequireStr('Operation')


    def VerifyCharge(self):
        '''👉 Verifies if all required properties are set.'''

        self.Require()
        self.RequireChargeID()
        
        operation = self.RequireOperation()
        
        UTILS.AssertIsAnyValue(
            value= operation, 
            options= ['DEBIT'], 
            msg='Valid operation?')

        amount = self.RequireAmount()
        if amount <= 0:
            LOG.RaiseException('Amount must be positive.')
        
        curency = self.RequireCurrency()
        if len(curency) != 3:
            LOG.RaiseException('Currency must ISO (3-letters).')
        
        collectors = self.Collectors()
        if len(collectors) == 0:
            LOG.RaiseException('At least one collector is required!')
        

    def MatchCollector(self, collector:str):
        '''👉 Verify if the collector is part of possible collectors.'''
        UTILS.Require(collector)
        
        myCollectors = self.Collectors()
        if collector not in myCollectors:
            LOG.RaiseValidationException(
                f'The collector=({collector}) is not part of the possible collectors={myCollectors}.')


    def MatchCharge(self, charge:CHARGE):
        '''👉 Verify if 2 charges have the same content.'''

        LOG.Print('🧾 CHARGE.MatchCharge()', 
                  'charge=', charge)
        
        UTILS.Require(charge)
        UTILS.AssertIsType(charge, CHARGE)

        UTILS.AssertEqual(
            given= charge.RequireAmount(), 
            expect= self.RequireAmount(), 
            msg='Amounts do not match.')
        
        UTILS.AssertEqual(
            given= charge.RequireCurrency(), 
            expect= self.RequireCurrency(), 
            msg='Currencies do not match.')
        
        UTILS.AssertEqual(
            given= charge.RequireOperation(), 
            expect= self.RequireOperation(), 
            msg='Operations do not match.')
        
        UTILS.AssertEqual(
            given= charge.RequireChargeID(), 
            expect= self.RequireChargeID(), 
            msg='ChargeIDs do not match.')
        
        UTILS.AssertEqual(
            given= charge.Collectors(), 
            expect= self.Collectors(), 
            msg='Collectors do not match.')