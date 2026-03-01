import boto3
from datetime import datetime, timezone, timedelta

# Initialize a boto3 client
lambda_client = boto3.client('lambda')

class LAMBDA_LAYERS():


    @classmethod
    def isoformat_to_datetime(cls, iso_str):
        """
        Convert an ISO 8601 string with timezone '+HHMM' or '-HHMM' to a datetime object.
        """
        # Split the string into the main part and the timezone part
        main_part, tz_offset = iso_str[:-5], iso_str[-5:]
        # Insert a colon into the timezone part to make it '+HH:MM' or '-HH:MM'
        tz_offset = tz_offset[:3] + ':' + tz_offset[3:]
        # Combine them back and convert to datetime
        return datetime.fromisoformat(main_part + tz_offset)
        
        
    @classmethod
    def ListOldLayers(cls, days_old:int= 1):
        '''👉 List all layer versions that are more than `days_old` days old.'''

        response = lambda_client.list_layers()
        old_layers = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)

        for layer in response.get('Layers', []):

            # List all versions of the layer
            versions_response = lambda_client.list_layer_versions(
                LayerName=layer['LayerName'])
            
            for version in versions_response.get('LayerVersions', []):
                
                created_date = version['CreatedDate']
                # Convert from string to datetime 
                created_date = cls.isoformat_to_datetime(created_date)  

                if created_date < cutoff_date:
                    old_layers.append({
                        'LayerName': layer['LayerName'], 
                        'Version': version['Version'], 
                        'VersionsCount': len(versions_response['LayerVersions'])
                    })

        return old_layers
    

    @classmethod
    def IsLayerUsed(cls, layer_name, layer_version):
        """
        👉 Check if a layer version is used by any lambda function.
        """
        response = lambda_client.list_functions()
        for function in response.get('Functions', []):
            layers = function.get('Layers', [])
            for layer in layers:
                if layer_name in layer['Arn'] and str(layer_version) in layer['Arn']:
                    return True
        return False


    @classmethod
    def DeleteUnusedOldLayers(cls, days_old:int= 1):
        '''👉 Retire old layer versions not used by any lambda function.'''

        # Get the list of old layers.
        old_layers = cls.ListOldLayers(
            days_old= days_old)

        # Loop the layers.
        for layer in old_layers:

            # Skip deletion if this is the only version of the layer
            if layer['VersionsCount'] <= 1:
                print(f"Skipping {layer['LayerName']} version {layer['Version']} as it's the only version available.")
                continue

            # Delete if not used.
            if not cls.IsLayerUsed(layer['LayerName'], layer['Version']):
                
                # Delete the layer version
                lambda_client.delete_layer_version(
                    LayerName=layer['LayerName'],
                    VersionNumber=layer['Version'])
                
                print(f"Deleted {layer['LayerName']} version {layer['Version']}")
