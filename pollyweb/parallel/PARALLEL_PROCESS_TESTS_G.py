

from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_PROCESS_TESTS_G(PARALLEL_TEST):

    ICON = '🧪'

    
    def IsThisFruitNice(self, fruit:str):
        pw.LOG.Print(self.IsThisFruitNice, f'({fruit})')

        return f'Yes, {fruit} is nice.'

    
    def TestFruitAnswers(cls):
        pw.LOG.Print(cls.TestFruitAnswers)

        pool = PARALLEL.PROCESS_POOL()

        pw.TESTS.AssertEqual(
            pool.GetLog().GetNameWithoutIcon(),
            f'{PARALLEL_PROCESS_TESTS_G.__name__}.'
            f'{cls.TestFruitAnswers.__name__}.md')
        
        result = pool.RunProcess(
            handler= cls.IsThisFruitNice,
            args= dict(
                fruit= 'apple2'))
        
        pw.TESTS.AssertEqual(result, 'Yes, apple2 is nice.')
        pw.TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        pw.TESTS.AssertEqual(pool.GetLog().GetIconName(), 'DONE')

        pw.LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        pw.LOG.Print(cls.TestAll)
        
        cls().TestFruitAnswers()

        pw.LOG.PARALLEL().SetClassDone()