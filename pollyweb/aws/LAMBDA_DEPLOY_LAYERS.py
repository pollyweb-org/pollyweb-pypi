from PW_UTILS.DIRECTORY import DIRECTORY
from LAMBDA_FUNCTION_DEPLOY import LAMBDA_FUNCTION_DEPLOY
from LOG import LOG
from PW_UTILS.UTILS import UTILS
from PW_UTILS.ZIP import ZIP


class LAMBDA_DEPLOY_LAYERS(LAMBDA_FUNCTION_DEPLOY):


    @classmethod
    def DeleteLayer(cls, name:str):
        ''' 👉 Deletes a Lambda Layer.'''

        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.DeleteLayer({name})', 
            f'{name=}')

        # Get the layer versions
        response = cls.Client().list_layer_versions(
            LayerName= name)
        
        # Delete each layer version
        for layer in response['LayerVersions']:
            cls.Client().delete_layer_version(
                LayerName= name,
                VersionNumber= layer['Version'])
            

    @classmethod
    def GetUsedLayerVersions(cls):
        used_versions = set()
        paginator = cls.Client().get_paginator('list_functions')

        # Iterate through all Lambda functions
        for page in paginator.paginate():
            for function in page['Functions']:
                layers = function.get('Layers', [])
                for layer in layers:
                    arn = layer['Arn']
                    # Extract version number from the ARN and check if it belongs to the target layer
                    if arn.startswith("arn:aws:lambda"):
                        parts = arn.split(':')
                        layer_name = parts[-2]
                        version_number = parts[-1]
                        used_versions.add((layer_name, version_number))
        
        return used_versions
    

    @classmethod
    def DeleteUnusedLayerVersions(cls, layerName:str):
        used_versions = cls.GetUsedLayerVersions()
        all_versions = cls.Client().list_layer_versions(LayerName=layerName)

        # Get the last version.
        lastVersion = 0
        for version in all_versions['LayerVersions']:
            version_number = version['Version']
            if version_number > lastVersion:
                lastVersion = version_number
    
        # Delete all unused versions, except the last.
        for version in all_versions['LayerVersions']:
            version_number = version['Version']

            # Ignore the last version.
            if lastVersion == version_number:
                continue

            layer_identifier = (layerName, str(version_number))

            if layer_identifier not in used_versions:
                # If the version is not used, delete it
                cls.Client().delete_layer_version(
                    LayerName=layerName,
                    VersionNumber=version_number)
                LOG.Print(
                    f'🦙 LAMBDA.DEPLOY.DeleteUnusedLayerVersions: '
                    f'Deleted unused version {version_number} of layer {layerName}')


    @classmethod
    def CreateLayer(cls, 
        dir:DIRECTORY, 
        layerName:str, 
        description:str=None
    ):
        ''' 👉 Creates a Lambda Layer from a directory.'''

        UTILS.AssertIsStr(layerName, require=True)
        UTILS.AssertIsStr(description, require=False)
        UTILS.AssertIsType(dir, DIRECTORY, require=True)

        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.CreateLayer({layerName})', 
            f'{layerName=}')

        # Verify the path.
        dir.AssertExists()

        # Verify the directory structure
        if not dir.ContainsDirectory('python'):
            LOG.RaiseException(
                f'Layer directory must contain a "python" directory.',
                f'Available directories: {dir.GetSubDirNames()}',
                dir)

        # Zip the directory
        zip = dir.Zip()

        # Verify if the layer already exists with the same code.
        existingZip = ZIP.LoadInfo(dir, layerName)
        if zip.IsSameAs(existingZip):
            return existingZip.RequireMetadata()

        # Get the zipped bytes.
        bytes = zip.GetBytes()

        # Publish the layer
        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.CreateLayer.publishing...')
        response = cls.Client().publish_layer_version(
            LayerName= layerName,
            Description= description or 'Created by the DTWF',
            Content= {
                'ZipFile': bytes
            },
            CompatibleRuntimes= [
                'python3.8',
                'python3.9',
                'python3.10',
                'python3.11',
            ])
        
        ret = {
            'Arn': response['LayerVersionArn'],
            'Version': response['Version'],
            'Directory': dir.GetPath(), 
            'Name': layerName, 
            'Description': description
        }

        # Save the ZIP info
        zip.GetZipInfo().Save(layerName, metadata=ret)
        
        # Return the ARN of the layer
        return ret

