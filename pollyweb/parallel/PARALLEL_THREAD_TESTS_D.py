

from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST


import PW_UTILS as pw


class PARALLEL_THREAD_TESTS_D(PARALLEL_TEST):

    ICON = '🧪'


    def _TestFailureAddTaskHelper(self):
        pw.UTILS.Sleep(0.3)
        return 1/0
    

    def _TestFailureAddTaskHelperTask3(self):
        pw.UTILS.Sleep(0.3)
        return 1/0
    
    
    def TestFailureAddTask(self):

        with pw.TESTS.AssertValidation(type= ZeroDivisionError):
            with PARALLEL.THREAD_POOL() as pool:

                task1 = pool.AddThread(
                    name= 'Task1',
                    handler= self._TestFailureAddTaskHelper)
                
                # Test this one with with the same method as task1. 
                task2 = pool.AddThread(
                    name= 'Task2',
                    handler= self._TestFailureAddTaskHelper)
                
                # Test this one without an explicit name, but different method.
                task3 = pool.AddThread(
                    handler= self._TestFailureAddTaskHelperTask3)
                
                # Test this one without an explicit name, same method.
                with pw.TESTS.AssertValidation(check='exists'):
                    pool.AddThread(
                        handler= self._TestFailureAddTaskHelperTask3)
                
                pool.RunAllThreads()

        # Verify the status of the pool.    
        pw.TESTS.AssertEqual(pool.GetLog().GetStatus(), 'FAILED')
        pw.TESTS.AssertEqual(pool.GetLog().GetIconName(), 'FAILED')
        pw.TESTS.AssertEqual(pool.GetLog().GetNameWithoutIcon(), 
            f'{PARALLEL_THREAD_TESTS_D.__name__}.'
            f'{PARALLEL_THREAD_TESTS_D.TestFailureAddTask.__name__}.md')
 
        # Verify the status of the tasks.
        pw.TESTS.AssertEqual(task1.GetStatus(), 'FAILED')
        #pw.TESTS.AssertEqual(task1.GetIconName(), 'FAILED')
        #pw.TESTS.AssertEqual(task1.GetNameWithoutIcon(), 
        #    f'{PARALLEL_THREAD_TESTS.__name__}.'
        #    f'{PARALLEL_THREAD_TESTS.TestFailureAddTask.__name__}.'
        #    f'Task1.md')

        # The second task should be failed.
        pw.TESTS.AssertEqual(task2.GetStatus(), 'FAILED')
        #pw.TESTS.AssertEqual(task2.GetIconName(), 'FAILED')
        #pw.TESTS.AssertEqual(task2.GetNameWithoutIcon(),
        #    f'{PARALLEL_THREAD_TESTS.__name__}.'
        #    f'{PARALLEL_THREAD_TESTS.TestFailureAddTask.__name__}.'
        #    f'Task2.md')
        
        # The third task should be failed.
        pw.TESTS.AssertEqual(task3.GetStatus(), 'FAILED')
        #pw.TESTS.AssertEqual(task3.GetIconName(), 'FAILED')
        #pw.TESTS.AssertEqual(task3.GetNameWithoutIcon(),
        #    f'{PARALLEL_THREAD_TESTS.__name__}.'
        #    f'{PARALLEL_THREAD_TESTS.TestFailureAddTask.__name__}.'
        #    f'{cls._TestFailureAddTaskHelperTask3.__name__}.md')
        
        pw.LOG.PARALLEL().SetMethodDone()
       
    
    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestFailureAddTask()
        
        pw.LOG.PARALLEL().SetClassDone()