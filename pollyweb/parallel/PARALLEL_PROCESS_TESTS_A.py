
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_PROCESS_TESTS_A(PARALLEL_TEST):

    ICON = '🧪'


    def IsThisFruitNice(self, fruit:str):
        try:
            pw.LOG.Print(self.IsThisFruitNice, f'({fruit})')
            pw.LOG.Print(f'Inside IsThisFruitNice.')

            return f'Yes, {fruit} is nice.' 
        
        except Exception as e:
            pw.LOG.Print(self.IsThisFruitNice, f'({fruit}): exception', e)
            return f'No, {fruit} is not nice. Exception: {str(e)}'


    def TestProcessStatus(self):
        pw.LOG.Print(self.TestProcessStatus)

        with PARALLEL.PROCESS_POOL() as pool:

            p = pool.StartProcess(
                handler= self.IsThisFruitNice,
                args= dict(
                    fruit= 'appleA'),
                )

            result = p.GetResult()
            pw.TESTS.AssertEqual(result, 'Yes, appleA is nice.')
        
        pw.TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        pw.TESTS.AssertEqual(pool.GetLog().GetIconName(), 'DONE')

        dir = pw.LOG.PARALLEL().SetMethodDone()
        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_A.',
            fileNames= [
                'TestProcessStatus',
                'TestProcessStatus.IsThisFruitNice'
            ],
            containsText= [
                'Yes, appleA is nice.'
            ])

        # For processes, only the process log contains the prints.
        # This is because the process has a separate memory space.
        self.AssertLineInLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_A.',
            fileNames= ['TestProcessStatus.IsThisFruitNice'],
            containsLine= 'Inside IsThisFruitNice.')


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestProcessStatus()
        
        pw.LOG.PARALLEL().SetClassDone()