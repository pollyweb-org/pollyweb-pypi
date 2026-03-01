from .PYTHON_EDITOR import PYTHON_EDITOR
from .TESTS import TESTS
from .LOG import LOG


class PYTHON_EDITOR_TEST:

    ICON='🐍'

    GIVEN=''''

    @classmethod
    def Method1(cls):
        LOG.Print('@')

    @classmethod
    def Method2(cls, dummy:int):
        LOG.Print(f'@')

    def Method3(self, dummy:int):
        LOG.Print('@')

    def Method4(self):
        LOG.Print('@', dummy)

    def Method5(self):
        LOG.Print('@: My message')

    def Method6(self):
        self.LOG().Print('@')

    @classmethod    
    def Method7(cls, arg:any):
        LOG.Print('@: bla')

    @classmethod    
    def Method8(cls, arg:any):
        LOG.Print('@: bla')

    def Method9(self):
        self.LOG().Print(f'@([{self.GetName()}])', self)

    def Method10(self):
        LOG.Print(f'@({exception=})', self)

    '''   

    EXPECTED=''''

    @classmethod
    def Method1(cls):
        LOG.Print(cls.Method1)

    @classmethod
    def Method2(cls, dummy:int):
        LOG.Print(cls.Method2)

    def Method3(self, dummy:int):
        LOG.Print(self.Method3)

    def Method4(self):
        LOG.Print(self.Method4, dummy)

    def Method5(self):
        LOG.Print(self.Method5, f': My message')

    def Method6(self):
        self.LOG().Print(self.Method6)

    @classmethod    
    def Method7(cls, arg:any):
        LOG.Print(cls.Method7, f': bla')

    @classmethod    
    def Method8(cls, arg:any):
        LOG.Print(cls.Method8, f': bla')

    def Method9(self):
        self.LOG().Print(self.Method9, f'([{self.GetName()}])', self)

    def Method10(self):
        LOG.Print(self.Method10, f'({exception=})', self)

    '''   

    @classmethod
    def TestRename(cls):
        
        result = PYTHON_EDITOR().FixCode(cls.GIVEN)
        #for line in result.splitlines(): print(line)
        TESTS.AssertEqual(result, cls.EXPECTED)


    @classmethod
    def TestAllEditor(cls):
        cls.TestRename()