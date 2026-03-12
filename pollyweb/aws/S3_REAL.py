# 📚 S3

import boto3
import os


s3 = boto3.client('s3')

BUCKET = os.environ['BUCKET_NAME']
KEY = os.environ['FILE_NAME']
    

class S3_REAL:


    @classmethod
    def GetText(cls, bucket=BUCKET, key=KEY) -> str:
        '''👉️ Reads the content and returns as an utf-8 string.'''
        return cls.ReadBytes(bucket, key).decode('utf-8')
            

    @classmethod
    def SetText(cls, text:str, bucket=BUCKET, key=KEY) -> str:
        '''👉️ Writes the content and returns the s3:// path.'''
        return cls.WriteBytes(text, bucket, key)
    

    @classmethod
    def ReadBytes(cls, bucket=BUCKET, key=KEY) -> bytes:
        '''👉️ Reads the content and returns as bytes.'''

        # Retrieve the S3 object
        response = s3.get_object(
            Bucket=bucket, 
            Key=key)

        # Read and return the data
        return response['Body'].read()
    

    @classmethod
    def WriteBytes(cls, content:bytes, bucket=BUCKET, key=KEY) -> str:
        '''👉️ Writes the content and returns the s3:// path.'''

        # Write to S3.
        s3.put_object(
            Body = content, 
            Bucket = bucket, 
            Key = key)
        
        # Return the location.
        return f's3://{bucket}{key}'
    

    @classmethod
    def Delete(cls, bucket, key) -> str:
        '''👉️ Deletes an object.'''
        s3.delete_object(
            Bucket = bucket, 
            Key = key)
    