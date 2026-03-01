from .PROFILER import PROFILER, PROFILER_RESULTS


class RUNNER:
    '''🧪 Test runner.'''
        

    @classmethod
    def ProcessProfiler(cls, res:PROFILER_RESULTS):
        '''👉 Processes the profiler.'''
        from .LOG import LOG
        LOG.GetLogDir().GetFile('profiler-by-total-time.txt').WriteText(res.ByTotalTime)
        LOG.GetLogDir().GetFile('profiler-by-avg-time.txt').WriteText(res.ByAvgTime)


    @classmethod
    def RunFromConsole(cls, 
        file:str, 
        name:str, 
        method:callable,
        testFast:bool=False
    ):
        print(f'🧪 RUNNER.RunFromConsole \n > {file=}\n > {name=} \n > {testFast=}')
        '''👉 Runs a test from the console.
        
        Arguments:
            * `file` {str} -- __file__.
            * `name` {str} -- __name__.
            * `method` {callable} -- Callback to run.

        Usage: 
            ```python
            TESTS.RunFromConsole(
                file=__file__, 
                name=__name__, 
                method= lambda: MyMethod(myArg1=myValue1))
            ```        
        '''

        if name != "__main__":
            print (f'⛔ Not running [{file}] as [{name}] is not __main__')
            return

        from .LOG import LOG
        LOG.Settings().SetTestFast(testFast)
        LOG.Init()
        LOG.Settings().SetWriteToConsole(True)

        # Dump the log settings.
        print('🧪 Log settings:', LOG.Settings().GetSettings())

        LOG.Print(f'Starting {file}...')

        try:

            with PROFILER(onRun= cls.ProcessProfiler):
                method()
            
            LOG.Buffer().SetDone()

        except Exception as e:
            LOG.Buffer().SetFail(e)
            raise

        finally:

            # Dump the database content
            try:
                from .DYNAMO_MOCK import DYNAMO_MOCK
                try: DYNAMO_MOCK.DumpToDir()
                except Exception as e: 
                    LOG.Print('😕 Unable to dump the database: ' + str(e))
            except ImportError:
                pass

            # Dump the wallet content
            try:
                from .WALLET import WALLET
                try: WALLET.DumpToFile()
                except Exception as e: 
                    LOG.Print('😕 Unable to dump the wallet: ' + str(e))
            except ImportError:
                pass

            # Dump the bucket content
            try:
                from .S3_MOCK import S3_MOCK
                try: S3_MOCK.DumpAll()
                except Exception as e: 
                    LOG.Print('😕 Unable to dump the bucket: ' + str(e))
            except ImportError:
                pass
            
            # Delete the temp folder if empty
            LOG.GetLogDir().GetSubDir('TEMP').DeleteIfEmpty()

            # Dump the main log
            LOG.Buffer().Stop()

            print('✅ RUNNER.RunFromConsole finished.')