from .PRINTABLE import PRINTABLE
import json

class PRINTABLE_DICT(PRINTABLE):


    def __init__(self, **kargs) -> None:
        self._dict = dict(kargs)
        super().__init__(self.ToJson)


    def ToJson(self):
        try:
            return self._dict
        except:
            return '<PRINTABLE_DICT: Error in ToJson>'