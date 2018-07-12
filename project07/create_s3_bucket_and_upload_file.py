import boto3
import os
import botocore
import boto3.session

my_bucket_name = "serverless-record-storage-lambda"
my_file_name = "report.xlsx"

print("Uploading '{}' to '{}'".format(my_file_name, my_bucket_name))

s3 = boto3.resource('s3')
s3client = boto3.client('s3')
try:
    s3.create_bucket(Bucket=my_bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
    print("Created new bucket: {}".format(my_bucket_name))
except botocore.exceptions.ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'BucketAlreadyExists':
        print("Bucket already exists.")
    elif error_code == 'BucketAlreadyOwnedByYou':
        print("Bucket already exists.")
    else:
        print('Error code: ' + e.response['Error']['Code'])
        print(e)

bucket = s3.Bucket(my_bucket_name)

with open("report.xlsx", 'rb') as data:
    s3client.upload_fileobj(data, 'serverless-record-storage-lambda', 'report.xlsx')
