import time
import json
import boto3

l = boto3.client('lambda')
role = {}
s3 = boto3.client('s3')



def create_function(name, zfile, lsize=512, timeout=10, update=False):
    """ Create, or update if exists, lambda function """
    triggername = "{0}-Trigger".format(name)
    role['Arn'] = 'arn:aws:iam::927310973816:role/ServerlessAdmin'
    with open(zfile, 'rb') as zipfile:
        if name in [f['FunctionName'] for f in l.list_functions()['Functions']]:
            if update:
                print('Updating %s lambda function code' % (name))
                return l.update_function_code(FunctionName=name, ZipFile=zipfile.read())
            else:
                print('Lambda function %s exists' % (name))
                for f in funcs:
                    if f['FunctionName'] == name:
                        lfunc = f
        else:
            print('Creating %s lambda function' % (name))
            lfunc = l.create_function(
                FunctionName=name,
                Runtime='python3.6',
                Role=role['Arn'],
                Handler='LoadPermitData.handler',
                Description='Lambda function to ingest a S3 excel spreadsheet',
                Timeout=timeout,
                MemorySize=lsize,
                Publish=True,
                Code={'ZipFile': zipfile.read()},
            )
            permissionResponse = l.add_permission(
                 FunctionName='LoadPermitData',
                 StatementId="{0}-Event".format(triggername),
                 Action='lambda:InvokeFunction',
                 Principal='s3.amazonaws.com',
                 SourceArn='arn:aws:s3:::serverless-record-storage-lambda'
            )
            print(permissionResponse)

            response = s3.put_bucket_notification_configuration(
                Bucket='serverless-record-storage-lambda',
                NotificationConfiguration = {'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': 'arn:aws:lambda:us-west-2:927310973816:function:LoadPermitData',
                    'Events': [
                        's3:ObjectCreated:*'
                    ]

                }
            ]})

        lfunc['Role'] = role
        return lfunc

name = 'LoadPermitData'

# Create a lambda function
lfunc = create_function(name, 'LoadPermitData.zip', update=True)


