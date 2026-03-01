# 📚 SECRETS

from SECRETS_SECRET import SECRETS_SECRET


class SECRETS_REAL:


    @classmethod
    def Get(cls, name:str) -> SECRETS_SECRET:
        secret = SECRETS_SECRET(name= name)
        return secret