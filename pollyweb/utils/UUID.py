from .STRUCT import STRUCT
from .UTILS import UTILS


class UUID(STRUCT):

    def MatchUUID(self):
        UTILS.AssertIsUUID(self.Obj())