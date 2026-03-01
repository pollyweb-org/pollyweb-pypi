
from .STRUCT import STRUCT


class LOG_BUFFER_INFO(STRUCT):


    @staticmethod
    def New(
        path:str,
        name:str,
        status:str,
        file=None
    ) -> None:
                
        info = LOG_BUFFER_INFO()
        
        from .FILE import FILE
        from .FILESYSTEM import FILESYSTEM
        if file is None:
            file2 = FILESYSTEM.FILE(path)
        else:
            file2 = file

        info.Obj(dict(
            FileNameWithoutIcon= file2.GetNameWithoutIcon(),
            FileIconName= file2.GetIconName(),
            FileSimpleName= file2.GetSimpleName(),
            Path= path,
            Name= name,
            Status= status
        ))

        return info


    @property
    def FileNameWithoutIcon(self) -> str:
        return self.RequireStr('FileNameWithoutIcon')
    

    @property
    def FileIconName(self) -> str:
        return self.RequireStr('FileIconName')
    

    @property
    def FileSimpleName(self) -> str:
        return self.RequireStr('FileSimpleName')
    

    @property
    def Path(self) -> str:
        return self.RequireStr('Path')
    

    @property
    def Name(self) -> str:
        return self.RequireStr('Name')
    
    
    @property
    def Status(self) -> str:
        return self.RequireStr('Status')
    