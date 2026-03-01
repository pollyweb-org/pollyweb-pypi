

from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST

import pollyweb.utils as pw


class PARALLEL_THREAD_TESTS_E(PARALLEL_TEST):

    ICON = '🧪'


    def TestWithoutRunning(self):
            
        # Without `with` nor `RunAllTasks()`, the task should be pending.
        pool1 = PARALLEL.THREAD_POOL(name='Pool1')
        task1 = pool1.AddThread(
            name= 'Task1',
            handler= lambda: 1/0)
        pw.TESTS.AssertEqual(task1.GetStatus(), 'PENDING')

        # With RunAllTasks() the task should be failed, regardless of `with`.
        pool2 = PARALLEL.THREAD_POOL(name='Pool2')
        task2 = pool2.AddThread(
            name= 'Task2',
            handler= lambda: 1/0)
        with pw.TESTS.AssertValidation(type= ZeroDivisionError):
            pool2.RunAllThreads()
        pw.TESTS.AssertEqual(task2.GetStatus(), 'FAILED')

        # With `with` the task should be failed, regardless of RunAllTasks().
        with PARALLEL.THREAD_POOL(name='Pool3') as pool3:
            task3 = pool3.AddThread(
                name= 'Task3',
                handler= lambda: 1/0)
            with pw.TESTS.AssertValidation(type= ZeroDivisionError):
                pool3.RunAllThreads()
        pw.TESTS.AssertEqual(task3.GetStatus(), 'FAILED')
            
        # With `with` the task should be failed, regardless of RunAllTasks().
        with pw.TESTS.AssertValidation(type= ZeroDivisionError):
            with PARALLEL.THREAD_POOL(name='Pool4') as pool4:
                task4 = pool4.AddThread(
                    name= 'Task4',
                    handler= lambda: 1/0)
        pw.TESTS.AssertEqual(task4.GetStatus(), 'FAILED')

        pw.LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        pw.LOG.Print(cls.TestAll)
        
        cls().TestWithoutRunning()
        
        pw.LOG.PARALLEL().SetClassDone()