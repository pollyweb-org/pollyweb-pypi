
from typing import Union
from .PRINTABLE import PRINTABLE


class LOG_EXCEPTION(PRINTABLE):


    def __init__(self, 
        exception: Exception,
        stackTrace: Union[str, list[str], None] = None
    ) -> None:
        
        self._exception = exception
        self._stackTrace = stackTrace
        self._type = type(exception).__name__
        self._name = str(exception)

        super().__init__(toJson= self.ToJson)


    def ToJson(self) -> any:
        return dict(
            Type= self._type,
            Exception= self._name)
    

    def GetName(self) -> str:
        return self._name