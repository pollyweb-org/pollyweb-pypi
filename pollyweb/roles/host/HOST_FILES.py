# 📚 HOST_FILE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from pollyweb import UTILS
from PW_AWS.AWS import AWS


class HOST_FILES():
    ''' 🪣 https://quip.com/s9oCAO3UR38A#temp:C:TDD026a3fce1988455796a1a4621 '''


    @classmethod
    def FILE(cls, obj):
        from HOST_FILE import HOST_FILE
        return HOST_FILE(obj)

    
    @classmethod
    def _table(cls):
        return AWS.DYNAMO('FILES')
    

    @classmethod
    def RequireFile(cls, fileID:str):
        item = cls._table().Require(fileID)
        ret = cls.FILE(item)
        ret.VerifyFile()
        return ret


    @classmethod
    def Insert(cls, broker, serialized, sessionID, name):
        
        # TODO: support files bigger than 400KB by storing them elsewhere.
        
        merge = cls.FILE({
            "ID": UTILS.UUID(),
            "Broker": broker,
            "SessionID": sessionID,        
            "Name": name,
            "Serialized": serialized
        })
        merge.VerifyFile()

        # Insert the file with a TTL
        cls._table().Insert(merge, days= 1)

