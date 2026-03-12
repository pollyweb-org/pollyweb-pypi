# 📚 VAULT_DISCLOSURE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.ITEM import ITEM
from MSG import MSG
from PW_AWS.AWS import AWS


class VAULT_DISCLOSURE(ITEM):
     ''' 🪣 https://quip.com/IZapAfPZPnOD#temp:C:PDZ71e7244be24842df9b773d541 
     {
          "Consumer": "any-host.org",
          "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",   
          "Timestamp": "2018-12-10T13:45:00.000Z",
          "Binds": [
               "BindID": "793af21d-12b1-4cea-8b55-623a19a28fc5",
               "Status": "@OTP",
               "Continue": "6704488d-fb53-446d-a52c-a567dac20d20"
          ]
     }'''
     

     @staticmethod
     def Disclosures():
          return AWS.DYNAMO('DISCLOSURES', keys=['Consumer', 'SessionID'])


     @staticmethod
     def GetDisclosure(msg:MSG) -> VAULT_DISCLOSURE:
          '''👉 Looks for the Disclose in the table.
          May return an empty struct - i.e., doesn't validate if exists.'''
          consumer = msg.RequireStr('Consumer')
          sessionID = msg.RequireStr('SessionID')

          item = VAULT_DISCLOSURE.Disclosures().GetItem({
               'Consumer': consumer,
               'SessionID': sessionID
          })
          # Note: don't validate if it exists.
          return VAULT_DISCLOSURE(item)

