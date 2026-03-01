from .PARALLEL import  PARALLEL
from .PARALLEL_PROCESS import PARALLEL_PROCESS
from .PARALLEL_PROCESS_POOL import PARALLEL_PROCESS_POOL
from .PARALLEL_TEST import PARALLEL_TEST
import pollyweb.utils as pw


class PARALLEL_PROCESS_TESTS_J(PARALLEL_TEST):

    ICON = '🧪'


    def IsThisFruitNice(self, fruit:str):
        pw.LOG.Print(self.IsThisFruitNice, f'({fruit})')

        return f'Yes, {fruit} is nice.'


    def TestProcessPool(self):
        pw.LOG.Print(self.TestProcessPool)

        with PARALLEL_PROCESS_POOL() as pool:

            # List of processes to assert later if are DONE.
            processes:list[PARALLEL_PROCESS] = []

            # Loop through the fruits (expected results).
            for fruit in ['orange', 'appleJ', 'banana']:

                # Start the process.
                p = pool.StartProcess(
                    name = fruit,
                    handler= self.IsThisFruitNice,
                    args= dict(
                        fruit= fruit
                    ))
                
                # Add to assert later if all are DONE.
                processes.append(p)

            # Get the results before the .Stop()
            results = pool.GetResults()

        # Assert all processes are DONE.
        for p in processes:
            pw.TESTS.AssertTrue(p.HasJoined())  

        result_keys = list(results.keys())
        pw.TESTS.AssertEqual(len(result_keys), 3)
        pw.TESTS.AssertEqual(result_keys, ['orange', 'appleJ', 'banana'])

        result_values = [
            results[fruit] for 
            fruit in results
        ]
        
        pw.TESTS.AssertEqual(
            result_values, [
                'Yes, orange is nice.',
                'Yes, appleJ is nice.',
                'Yes, banana is nice.'
            ])
        
        pw.TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        pw.TESTS.AssertEqual(pool.GetLog().GetIconName(), 'DONE')  

        pw.LOG.PARALLEL().SetMethodDone()
            

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        pw.LOG.Print(cls.TestAll)
        
        cls().TestProcessPool()

        pw.LOG.PARALLEL().SetClassDone()