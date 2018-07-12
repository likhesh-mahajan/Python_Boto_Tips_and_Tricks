import boto3
import os
import sys
import uuid
import pandas as pd

s3_client = boto3.client('s3')
bucket = "serverless-record-storage-lambda"


def upload_to_dynamodb(report):
    df=pd.read_excel(report)
    df.columns=["APPLICATION", "FORM_NUMBER", "FILE_DATE", "STATUS_DATE", "STATUS", "STATUS_CODE", "EXPIRATION_DATE", "ESTIMATED COST", "REVISED_COST", "EXISTING_USE", "EXISTING_UNITS", "PROPOSED_USE","PROPOSED_UNITS","PLANSETS", "15_DAY_HOLD?" ,  "EXISTING_STORIES", "PROPOSED_STORIES", "ASSESSOR_STORIES", "VOLUNTARY", "PAGES", "BLOCK", "LOT", "STREET_NUMBER", "STREET_NUMBER_SFX", "AVS_STREET_NAME", "AVS_STREET_SFX", "UNIT", "UNIT_SFX", "FIRST_NAME", "LAST_NAME", "CONTRACTORPHONE",
        "COMPANY_NAME", "STREET_NUMBER", "STREET", "STREET_SUFFIX", "CITY", "STATE", "ZIP_CODE", "CONTACT_NAME", "CONTACT_PHONE", "DESCRIPTION" ]
    # Clean-up the data, change column types to strings to be on safer side :)
    df=df.replace({'-': '0'}, regex=True)
    df=df.fillna(0)
    for i in df.columns:
        df[i] = df[i].astype(str)
    # Convert dataframe to list of dictionaries (JSON) that can be consumed by any no-sql database
    myl=df.T.to_dict().values()
    # Connect to DynamoDB using boto
    resource = boto3.resource('dynamodb', region_name='us-west-2')
    # Connect to the DynamoDB table
    table = resource.Table('permitdata')
    # Load the JSON object created in the step 3 using put_item method
    for permit in myl:
        table.put_item(Item=permit)

def handler(event, context):
    for record in event['Records']:
        print(record)
        bucket = record['s3']['bucket']['name']
        print(bucket)
        key = record['s3']['object']['key']
        print(key)
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

        s3_client.download_file(bucket, key, download_path)
        upload_to_dynamodb(download_path)



def main():
    handler(event, None)

if __name__ == "__main__":
    main()
