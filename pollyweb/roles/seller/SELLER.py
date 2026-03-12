# 💵 SELLER

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from MSG import MSG
from PW import PW
from SESSION import SESSION
from CHARGE import CHARGE
from SELLER_CHARGE import SELLER_CHARGE
from pollyweb import UTILS
from PW_UTILS.HANDLER import HANDLER
from pollyweb import LOG

   
# ✅ DONE
class SELLER(HANDLER):
    ''' 💵 Seller
    * https://quip.com/U03QASVxXbhG 

    Methods:
    * `AddCollector`: adds to 🪣Collectors.
    * `Charge`: adds to 🪣Charges and invokes 🐌Charge@Broker.
    * `InvokePaid`: invokes Paid@Seller.
    '''


    @classmethod
    def COLLECTORS(cls):
        from SELLER_COLLECTOR import SELLER_COLLECTOR
        return SELLER_COLLECTOR()
    

    def AddCollector(self, collector:str):
        '''👉 Adds to 🪣Collectors.
        Required as a set up for a seller.
        Whithout this, the CHARGE struct will fail to validate.'''
        self.COLLECTORS().Insert(collector)
        

    @classmethod
    def Charge(cls, source:str, session:SESSION, message:str, amount:float, currency:str):
        '''😃🏃 adds to 🪣Charges and invokes 🐌Charge@Broker.'''

        LOG.Print(
            '💵 SELLER.Charge()', 
            f'{source=}', f'{message=}', f'{amount=}', f'{currency=}')

        UTILS.RequireArgs([source, message, session, amount, currency])
        UTILS.AssertIsType(session, SESSION)

        session.VerifySession()

        # Get the list of active collectors.
        collectors = cls.COLLECTORS().ActiveOnes()
        
        # Register the charge.
        sellerCharge = SELLER_CHARGE.Insert(
            amount= amount,
            currency = currency,
            collectors= collectors)

        # Charge the broker.
        PW.ROLES().BROKER().InvokeCharge(
            source= source,
            message= message,
            session= session,
            charge= sellerCharge.ToCharge())
        

    @classmethod
    def MatchCharge(cls, seller:str, charge:CHARGE):
        ''' Verify if the charge is still valid.'''

        LOG.Print(
            '💵 SELLER.MatchCharge()', 
            f'{seller=}', 
            'charge=', charge)
        
        UTILS.RequireArgs([seller, charge])
        UTILS.AssertIsType(seller, str)
        UTILS.AssertIsType(charge, CHARGE)
        
        sellerCharge = cls.InvokeIsCharged(
            seller= seller,
            chargeID= charge.RequireChargeID())
        
        charge.MatchCharge(sellerCharge)


    @classmethod
    def InvokeIsCharged(cls, seller:str, chargeID:str) -> CHARGE:

        LOG.Print('💵 SELLER.InvokeIsCharged()', 
                  f'{seller=}', f'{chargeID=}')

        UTILS.RequireArgs([seller, chargeID])

        ret = PW.BEHAVIORS().SYNCAPI().Invoke(
            to= seller, 
            subject= 'IsCharged@Seller',
            body= {
                "ChargeID": chargeID
            })
        
        ret = CHARGE(ret)
        ret.VerifyCharge()
        return ret
    

    @classmethod
    def HandleIsCharged(cls, event):
        ''' 
        "Body": {
            "ChargeID": <uuid>
        }'''

        LOG.Print('💵 SELLER.HandleIsCharged()', event)

        msg = MSG(event)
        chargeID = msg.RequireUUID('ChargeID')
        charge = SELLER_CHARGE.RequireCharge(chargeID)
        ret = charge.ToCharge()
        ret.VerifyCharge()
        return ret


    @classmethod
    def InvokePaid(cls, source:str, session:SESSION, charge:CHARGE, transaction:any):
        ''' 🏦🏃 COLLECTOR invokes Paid@Seller'''
        
        LOG.Print('💵 SELLER.HandlePaid()', 
                  f'{source=}', 
                  'session=', session,
                  'charge=', charge, 
                  'transaction=', transaction)

        UTILS.RequireArgs([source, session, charge, transaction])

        PW.BEHAVIORS().MESSENGER().Push(
            source= source, 
            to= session.RequireHost(), 
            subject= 'Paid@Seller',
            body= {
                "Session": session,
                "Charge": charge,
                "Transaction": transaction
            })


    @classmethod
    def HandlePaid(cls, event):
        ''' 🏦🐌 https://quip.com/U03QASVxXbhG#temp:C:IBP77a2c2d4ac1f4a9d84dad87d6
        "Body": {
            "Session": {...},
            "Charge": {...},
            "Transaction": {...}
        }'''

        LOG.Print('💵 SELLER.HandlePaid()', event)

        # Parse the message.
        msg = MSG(event)
        charge = msg.RequireStruct('Charge')
        session = msg.RequireStruct('Session')
        transaction = msg.RequireStruct('Transaction')

        # Verify if the session is valid.
        session = PW.ROLES().HOST().SESSIONS().RequireSession(
            broker= msg.RequireDeepStr('Session.Broker'),
            sessionID= msg.RequireDeepUUID('Session.SessionID'))

        # Verify if the message is trustable.
        inCharge = CHARGE(charge)
        inCharge.VerifyCharge()
        inCharge.MatchCollector(collector= msg.RequireFrom())

        # Verify if the collector is still active.
        collector = cls.COLLECTORS().RequireDomain(msg)
        collector.VerifyIsActive()

        ''' 🔒 Let's not expose the agreements between seller/collector.
        # Verify if the collector is still trustable.
        PW.ROLES().GRAPH().VerifyTrust(
            domain= collector.Domain(),
            context= 'VAULT',
            code= CODE.COLLECTOR())
        '''

        # Verify if the charge exists and it was not changed.
        inChargeID = inCharge.RequireChargeID()
        dbCharge = SELLER_CHARGE.RequireCharge(inChargeID)
        dbCharge.MatchCharge(inCharge)
        dbCharge.VerifyNotPaid()

        # Save the payment.
        dbCharge.Pay(
            collector=collector, 
            transaction=transaction)

        # Trigger additional tasks.
        cls.Trigger('OnPaid@Seller', dbCharge)

        # Continue the conversation.
        session.ContinueTalk(msg)
