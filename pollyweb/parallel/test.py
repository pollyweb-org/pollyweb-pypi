import PW_UTILS as pw
print (pw.LOG.hello())

from .TEST_PARALLEL import TEST_PARALLEL

pw.RUNNER.RunFromConsole(
    file= __file__,
    name= __name__, 
    testFast= False,
    method= TEST_PARALLEL.TestParallel)