from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from CODEBUILD_BUILD import CODEBUILD_BUILD
from pollyweb.utils.LOG import LOG
from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.STRUCT import STRUCT


class CODEBUILD_PROJECT(AWS_RESOURCE_ITEM):

    ICON = '🏗️'
    

    def __init__(self, 
        meta: dict,
        pool: AWS_RESOURCE_POOL,
        client
    ):
        '''👉 Initializes a new instance of the CODEBUILD_PROJECT class.
        
        meta: dict - The project metadata.
        client - The AWS CodeBuild client.'''
        
        LOG.Print('@')

        meta:STRUCT = STRUCT(meta)
        
        self.Meta = meta
        self.Client = client
        self.Name = meta['name']
        self.Arn = meta['arn']
        #self.Id = meta['id']
        self.Source = meta['source'] if 'source' in meta else None
        self.Artifacts = meta['artifacts'] if 'artifacts' in meta else None
        self.Environment = meta['environment'] if 'environment' in meta else None

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool,
            client= client, 
            arn= self.Arn,
            name= self.Name)

        PRINTABLE.__init__(self, {
            'Name': self.Name,
            'Arn': self.Arn,
            #'Id': self.Id,
            'Source': self.Source,
            'Artifacts': self.Artifacts,
            'Environment': self.Environment
        })


    def _Delete(self):
        '''👉 Deletes the project.'''
        self.Client.delete_project(name= self.Name)
    

    def StartBuild(self):
        '''👉 Starts a build.'''
        LOG.Print('@', self)
        
        build_response = self.Client.start_build(
            projectName= self.Name)
        
        return CODEBUILD_BUILD(
            client= self.Client,
            meta= build_response['build'])
    
   
    def Update(self,
        source: dict= None,
        artifacts: dict= None,
        environment: dict= None
    ):
        '''👉 Updates the project.'''
        LOG.Print('@', self)
        
        update_response = self.Client.update_project(
            name= self.Name,
            source= source if source else self.Source,
            artifacts= artifacts if artifacts else self.Artifacts,
            environment= environment if environment else self.Environment)
        
        return CODEBUILD_PROJECT(
            update_response['project'], 
            pool= self.Pool,
            client= self.Client)
    
