# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

import json
from PW_UTILS.HANDLER import HANDLER
from MSG import MSG
from NLWEB import NLWEB
from PW_AWS.ITEM import ITEM
from pollyweb import STRUCT
from PW_AWS.AWS import AWS



class PUBLISHER_CORRELATION(ITEM):    
    ''' Used for dedups
    {
        "Domain": "example.com",
        "Correlation": "2018-12-10T13:45:00.000Z"
    }'''
    

    @staticmethod
    def _table():
        return AWS.DYNAMO('CORRELATIONS', keys=['Domain', 'Correlation'])
    
    
    @staticmethod
    def GetCorrelation(msg:MSG) -> PUBLISHER_CORRELATION:
        correlation = PUBLISHER_CORRELATION().New(msg)
        item = PUBLISHER_CORRELATION._table().GetItem(correlation)
        # Note: don't verify existance.
        return PUBLISHER_CORRELATION(item)
    

    def New(self, msg:MSG) -> PUBLISHER_CORRELATION:
        self.Obj({
            'Domain': msg.RequireFrom(),
            'Correlation': msg.RequireCorrelation()
        })
        return self


    @staticmethod
    def Insert(msg:MSG) -> PUBLISHER_CORRELATION:
        ''' save to Correlations table.'''
        correlation = PUBLISHER_CORRELATION().New(msg)
        PUBLISHER_CORRELATION._table().Insert(correlation, days=1)
        return correlation