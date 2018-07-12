import boto3

class DynamoDB(object):
    def __init__(self, *args, **kwargs):
        #self.tablename = tablename
        self.__dict__.update(kwargs)

    # Query client and list_tables to see if table exists or not
    def QueryCreate(self, tablename):
        # Instantiate your dynamo client object
        client = boto3.client('dynamodb')

        # Get an array of table names associated with the current account and endpoint.
        response = client.list_tables()

        if tablename in response['TableNames']:
            table_found = True
        else:
            table_found = False
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

            # Create the DynamoDB table from the variable tablename
            table = dynamodb.create_table(
                TableName = tablename,
                KeySchema=[
                    {
                        'AttributeName': 'LAST_NAME',
                        'KeyType': 'HASH'  #Partition key
                    },
                    {
                        'AttributeName': 'APPLICATION',
                        'KeyType': 'RANGE'  #Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'LAST_NAME',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'APPLICATION',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )

            # Wait until the table exists.
            table.meta.client.get_waiter('table_exists').wait(TableName=tablename)
        return table_found

permitsdb = DynamoDB()
permitsdb.QueryCreate(tablename="permitdata")


