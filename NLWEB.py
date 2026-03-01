import os


class _NLWEB_CONFIG:
    _domain = os.getenv("POLLYWEB_DOMAIN", "*")

    @classmethod
    def SetDomain(cls, domain: str):
        if domain is None:
            return
        cls._domain = domain

    @classmethod
    def RequireDomain(cls) -> str:
        try:
            from pollyweb.aws.DYNAMO_MOCK import DYNAMO_MOCK

            active = getattr(DYNAMO_MOCK, "_activeDomain", None)
            if active:
                cls._domain = active
        except Exception:
            pass

        return cls._domain


class NLWEB:
    @classmethod
    def CONFIG(cls):
        return _NLWEB_CONFIG

    @classmethod
    def AWS(cls):
        from pollyweb.aws.AWS import AWS

        return AWS()
