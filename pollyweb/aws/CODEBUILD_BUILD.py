from pollyweb.utils.LOG import LOG
from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.UTILS import UTILS


class CODEBUILD_EMPTY_REPO_EXCEPTION(Exception):
    '''👉 Raised when the CodeBuild repository is empty.'''
    pass


class CODEBUILD_BUILD(PRINTABLE):

    ICON = '🏗️'
    

    def __init__(self, client, meta:dict):
        '''👉 Initializes a new build.'''
        LOG.Print('@')

        self.ID = meta['id']
        self.ProjectName = meta['projectName']
        self.Meta = meta
        self.Client = client

        PRINTABLE.__init__(self, lambda: {
            'ID': self.ID
        })


    def Stop(self):
        '''👉 Stops a build.'''
        LOG.Print('@', self)
        
        self.Client.stop_build(
            id= id)
        return self
    

    def WaitToComplete(self, checkIntervalSeconds:int= 2):
        '''👉 Polls CodeBuild to get the current status of the build until it's no longer in progress.
            * Raises an exception if the build fails with details about the failure.'''
    
        while True:
            LOG.Print(f"@: Getting build status...")
            response = self.Client.batch_get_builds(
                ids=[self.ID])
            
            build_info = response['builds'][0]
            build_status = build_info['buildStatus']
            log_location = build_info.get('logs', {}).get('deepLink', 'No log details available.')
            
            if build_status not in ['IN_PROGRESS', 'QUEUED']:
                
                if build_status == 'SUCCEEDED':
                    LOG.Print(f"Build completed successfully with status: {build_status}")
                    return build_status
                
                # Check each phase for errors
                for phase in build_info['phases']:
                    phase_type = phase['phaseType']
                    phase_status = phase.get('phaseStatus', 'SUCCEEDED')
                    
                    if phase_status != 'SUCCEEDED':
                        # Print error details
                        contexts = phase.get('contexts', [])
                        for context in contexts:
                            message = context.get('message', 'No error message provided.')

                            if 'repository is empty' in message:
                                raise CODEBUILD_EMPTY_REPO_EXCEPTION(f"@: Error in {phase_type}: {message}")
                            
                            LOG.RaiseException(
                                f"@: Error in phase {phase_type}: {message}.\n"
                                f"@: Check the logs at {log_location}. ")

                # Attempt to fetch logs and error details
                LOG.RaiseException(f"@: Build failed with status {build_status}. Check the logs at: {log_location}")
        
            LOG.Print(f"@: Build is {build_status}...")
            UTILS.Sleep(seconds= checkIntervalSeconds)  # Poll every N seconds