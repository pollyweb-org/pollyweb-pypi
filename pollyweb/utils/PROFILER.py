import cProfile
import pstats
import io


class PROFILER_RESULTS:
    '''🧪 Profiler results.'''

    def __init__(self, byTotalTime:str, byAvgTime:str):
        self.ByTotalTime = byTotalTime
        self.ByAvgTime = byAvgTime


class PROFILER:
    '''🧪 Profiler to measure of the performance of python functions.'''

    def __init__(self, onRun:callable):
        '''👉 Constructor.

        Arguments:
            * `onRun` {callable} -- Callback to run with the profile results.
        '''
        self.onRun = onRun


    def __enter__(self):
        '''👉 Enter the profiler.'''
        self.pr = cProfile.Profile()
        self.pr.enable()


    def _GetStats(self, sort:str):
        '''👉 Get the profiler stats.
        
        Arguments:
            * `sort` {str} -- Sort by.
        '''
        s = io.StringIO()
        ps = pstats.Stats(self.pr, stream=s)
        ps.strip_dirs()
        ps.sort_stats(sort)
        ps.print_stats()
        return s.getvalue()


    def __exit__(self, *args):
        '''👉 Exit the profiler.'''
        self.pr.disable()

        byTotalTime = self._GetStats('cumulative')
        byAvgTime = self._GetStats('time')

        self.onRun(PROFILER_RESULTS(
            byTotalTime= byTotalTime,
            byAvgTime= byAvgTime))