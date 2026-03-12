# 📚 DYNAMO

from LOG import LOG

import boto3
dynamoClient = boto3.client('dynamodb')


class DYNAMO_BACKUP:
    '''👉 Management of Dynamo backups.'''


    @classmethod
    def GetAllTableNames(cls) -> list[str]:
        '''👉 List all DynamoDB tables.'''
        LOG.Print(f'GetAllTableNames()')

        ret = dynamoClient.list_tables()['TableNames']
        LOG.Print(f'GetAllTableNames.return: {ret=}')
        return ret


    @classmethod
    def BackupTable(cls, table_name):
        '''👉 Creates a backup for the table.'''
        LOG.Print(f'BackupTable({table_name=})')
        
        from datetime import datetime
        backup_name = f"Backup-{table_name}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

        try:
            dynamoClient.create_backup(
                TableName=table_name,
                BackupName=backup_name)
            LOG.Print(f"Backup created for table {table_name}: {backup_name}")
            
        except Exception as e:
            if type(e).__name__ == 'ContinuousBackupsUnavailableException':
                LOG.Print(f"PITR is being enabled on {table_name}.")
            

    @classmethod
    def GetAllTableBackups(cls, table_name) -> list[dict]:
        '''👉 List all DynamoDB tables.'''
        
        return dynamoClient.list_backups(TableName=table_name)['BackupSummaries']
        '''returns {
            BackupArn: str,
            BackupCreationDateTime: datetime
        }'''
    

    @classmethod
    def KeepRetention(cls, table_name:str, retention_days:int=1) -> None:
        '''👉 Cleans up old backups.'''
        LOG.Print(f'KeepRetention({table_name=}, {retention_days=})')
        
        # List backups for the table
        backups = cls.GetAllTableBackups(table_name)

        # Current time in UTC
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)

        # Delete backups older than retention
        if not retention_days:
            for backup in backups:
                backup_age = now - backup['BackupCreationDateTime']
                if backup_age > timedelta(days= retention_days):
                    dynamoClient.delete_backup(
                        BackupArn= backup['BackupArn'])
                    LOG.Print(
                        f"Deleted backup {backup['BackupArn']} for table {table_name}")


    @classmethod
    def BackUpAll(cls, retention_days:int=1) -> None:
        '''👉 Backs up all dynamoDB tables.
         * Removes backups with more than the retention days.
         * Keeps backups indefinitly for tables that no longer exist.
        ''' 
        LOG.Print(f'BackUpAll({retention_days=})')
        
        for table_name in cls.GetAllTableNames():
            cls.BackupTable(
                table_name= table_name)
            cls.KeepRetention(
                table_name= table_name,
                retention_days= retention_days) 
                
        LOG.Print(f'BackUpAll.done')