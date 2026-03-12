# 🤝 PW


class PW_INTERFACES:

    @classmethod
    def CODE(cls, item:any=None):
        from PW_DOMAIN import CODE as proxy
        return proxy(item)
    
    @classmethod
    def TOKEN(cls, item:any=None):
        from TOKEN import TOKEN as proxy
        return proxy(item)
    
    @classmethod
    def MANIFEST(cls, manifest:any = None):
        ''' 👉 Wrapper of a YAML Manifest. '''
        from PW_DOMAIN import MANIFEST as proxy
        return proxy(manifest)

    @classmethod
    def MSG(cls, event:any):
        from MSG import MSG
        return MSG(event)

    @classmethod
    def PROMPT(cls, obj:dict=None):
        from PROMPT import PROMPT
        return PROMPT(obj)

    @classmethod
    def SESSION(cls, obj:any):
        from SESSION import SESSION
        return SESSION(obj)
    
    @classmethod
    def UPDATE(cls, item:any=None):
        from UPDATE import UPDATE as proxy
        return proxy(item)

