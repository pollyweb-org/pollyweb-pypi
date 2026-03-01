from pollyweb.utils.DIRECTORY import DIRECTORY
from pollyweb.utils.LOG import LOG
from S3_URL import S3_URL
from pollyweb.utils.STRUCT import STRUCT

from pollyweb.utils.UTILS import UTILS


class S3_MOCK:

    @classmethod
    def URL(cls, uri:str):
        return S3_URL(uri)
    
    BUCKET = 'NLWEB'

    _domains:dict[str,dict[str,dict]] = {}


    @classmethod
    def GetBucket(cls, bucket):

        from NLWEB import NLWEB
        domain = NLWEB.CONFIG().RequireDomain()

        if domain not in S3_MOCK._domains:
            S3_MOCK._domains[domain] = {}

        if bucket not in S3_MOCK._domains[domain]:
            S3_MOCK._domains[domain][bucket] = {}

        ret = S3_MOCK._domains[domain][bucket]
        return STRUCT(ret)


    @classmethod
    def GetText(cls, key:str, bucket=BUCKET) -> str:
        '''👉️ Reads the content and returns as an utf-8 string.'''
        key = key.lstrip('/')
        return cls.GetBucket(bucket).RequireStr(key, noHierarchy=True)
            

    @classmethod
    def SetText(cls, text:str, key:str, bucket=BUCKET) -> str:
        '''👉️ Writes the content and returns the s3:// path.'''

        key = key.lstrip('/')
        return cls.WriteBytes(
            content= text, 
            bucket= bucket, 
            key= key)
    

    @classmethod
    def ReadBytes(cls, key:str, bucket=BUCKET) -> bytes:
        '''👉️ Reads the content and returns as bytes.'''
        LOG.Print('🪣 S3.MOCK.ReadBytes()', f'{key=}', f'{bucket=}')

        key = key.lstrip('/')
        files = cls.GetBucket(bucket)

        # Retrieve the S3 object
        if key not in files:
            LOG.RaiseException(
                f'Key not found!', 
                f'{bucket=}', 
                f'{key=}',
                f'keys={files.keys()}')

        response = files[key]
        UTILS.AssertIsType(response, bytes)

        # Read and return the data
        return response
    

    @classmethod
    def WriteBytes(cls, content:bytes, key:str, bucket=BUCKET) -> str:
        '''👉️ Writes the content and returns the s3:// path.'''

        key = key.lstrip('/')

        # Write to mock S3.
        cls.GetBucket(bucket)[key] = content
        
        # Return the location.
        return f's3://{bucket}/{key}'
    

    @classmethod
    def Delete(cls, key:str, bucket=BUCKET) -> str:
        '''👉️ Deletes an object.'''

        key = key.lstrip('/')
        cls.GetBucket(bucket).RemoveAtt(key)


    @classmethod
    def DumpAll(cls, dir:DIRECTORY = None):
        LOG.Print(f'@', dir)
        
        if dir == None:
            dumps = UTILS.OS().CurrentDirectory()
            dumps = dumps.GetSubDir('__dumps__').Touch()
            dir = dumps.GetSubDir('S3').Touch()

        for d in S3_MOCK._domains:
            LOG.Print(f'🪣 MOCK.S3.DumpToFile:', 
                  f'domain= {d}')
            domain = dir.GetSubDir(d).Touch()
            for bucket in S3_MOCK._domains[d]:
                files = S3_MOCK._domains[d][bucket]
                domain.GetFile(f'{bucket}@{d}.yaml').WriteYaml(files)