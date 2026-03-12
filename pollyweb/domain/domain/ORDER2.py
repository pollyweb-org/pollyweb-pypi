from __future__ import annotations

from pollyweb import UTILS
from PW_AWS.ITEM import ITEM
from MSG import MSG


class ORDER2(ITEM):
    ''' 🪣 https://quip.com/U97qAoGmSPAn#temp:C:HKU829fc252784b4a85a190e1e37
    {
        "OrderID": "2045c157-1a86-4a7f-b620-81f66e493a01",
        "Timestamp": "2018-12-10T13:45:00.000Z",
        "Owner": "any-domain.com",
        "Items": [...],
        "Booking": {...},
        "Delivery": {...},
        "Billing": {...}
    }
    '''

    @staticmethod
    def _table():
        return DYNAMO('ORDERS')
    

    @staticmethod
    def Insert(msg:MSG) -> ORDER:
        item = {
            "OrderID": UTILS.UUID(),
            "Timestamp": UTILS.GetTimestamp(),
            "Owner": msg.RequireFrom(),
            "Items": msg.RequireAtt('Items'),
            "Booking": None,
            "Delivery": None,
            "Billing": None,
            "Charge": None,
            "Payment": None
        }
        ORDER._table().Insert(item)
        return ORDER(item)
    
    