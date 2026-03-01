from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from PW_UTILS.DIRECTORY import DIRECTORY
from PW_UTILS.LOG import LOG
from PW_UTILS.PRINTABLE import PRINTABLE
from PW_UTILS.PYTHON_APP import PYTHON_APP
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS


class ECR_REPO(
    AWS_RESOURCE_ITEM, 
    PRINTABLE
):


    def __init__(self, 
        pool: AWS_RESOURCE_POOL,
        client,
        meta:dict,
        resource=None,
    ):
        '''👉 Initializes the repository.'''

        from ECR import ECR
        assert pool == ECR
        
        self.Name:str = meta['repositoryName']
        self.Arn:str = meta['repositoryArn']
        self.ID:str = meta['registryId']
        self.CreatedAt = meta['createdAt']
        self.ImageScanningConfiguration = meta['imageScanningConfiguration']
        self.ImageTagMutability = meta['imageTagMutability']
        self.LifecyclePolicy = meta['lifecyclePolicy'] if 'lifecyclePolicy' in meta else None
        self.RepositoryUri:str = meta['repositoryUri']
        self.EncryptionConfiguration = meta['encryptionConfiguration']
        self.Tags = meta['tags'] if 'tags' in meta else None

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool,  
            client= client, 
            resource= resource,
            name= self.Name,
            arn= self.Arn)

        PRINTABLE.__init__(self, dict(
            Name= self.Name,
            Arn= self.Arn
        ))


    def _Delete(self, 
        force:bool=True # Set to True to force deletion even if the repo is not empty
    ):
        LOG.Print('@', self)
        self.Client.delete_repository(
            repositoryName= self.Name,
            force= force)
        

    def _BuildDocker(self,
        builder:callable,
        source:DIRECTORY
    ):
        from AWS import AWS
        from PW_UTILS.UTILS import UTILS
        
        # Create a CodeBuild project that builds a Docker project
        with AWS.CODECOMMIT().Ensure(
            name= self.Name + '-' + UTILS.TIME().SecondsStr()
        ) as repo:
            
            with repo.Clone() as clone:
                clone.RetainOnFailure = self.RetainOnFailure
                clone.Retain = self.Retain
                
                # Import the source directory into the CodeCommit repository
                clone.ImportDirectory(
                    source= source)
                
                # Add the Docker build files to the CodeCommit repository.
                builder(clone)

                # We need to sync manually because the build is inside the scope.
                # If the build was outside the scope, the sync would be done automatically.
                # This is to be able to preserve the directory for debugging.
                clone.Sync()
            
                # Build the Docker project
                repo.Build()

        # Delete old images.
        self.DeleteNonLatestImages()

        return self


    

    def GetImageUri(self):
        '''👉 Gets the list of images in the repository.'''
        response = self.Client.describe_images(
            repositoryName= self.Name)
        
        for image in response['imageDetails']:
            if image['imageTags']:
                name = image['imageTags'][0]
                if name == 'latest':
                    return self.RepositoryUri + ':' + name
    
        return None
    

    def HasImage(self):
        '''👉 Checks if the repository has an image.'''
        return self.GetImageUri() != None
    

    def DeleteNonLatestImages(self):
        '''👉 Deletes all images except the latest.'''
        LOG.Print('@', self)

        response = self.Client.describe_images(
            repositoryName= self.Name)
        
        response = STRUCT(response)
        
        for image in response.RequireList('imageDetails'):
            image = STRUCT(image)
            
            if image.ContainsAtt('imageTags'):
                name = image['imageTags'][0]
                if name == 'latest':
                    continue

            self.Client.batch_delete_image(
                repositoryName= self.Name,
                imageIds=[{'imageDigest': image['imageDigest']}])  