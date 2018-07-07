#!/usr/bin/env python
import logging
import boto3
import collections
import sys
import pprint
import time
import os
import json
import operator
from datetime import datetime, timedelta, tzinfo


logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)


session = boto3.Session(profile_name='default')
ec2_client = session.client('ec2', region_name='us-east-1')
regions = ec2_client.describe_regions()['Regions']
now = time.strftime("%x")
response = ec2_client.describe_instances()


def create_images(response):
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance['InstanceId']
            currenttime = str(now)
            name = "AMI for {instance_id} {currenttime}".format(instance_id=instance_id,currenttime=currenttime)
            print("creating image for instance {instance_id}".format(instance_id=instance_id))
            ec2_client.create_image(InstanceId=instance_id,Name=name,NoReboot=True, DryRun=False)

def tag_snapshots():
    for region in regions:
        region_name = region['RegionName']
        ec2_client = session.client('ec2', region_name=region_name)
        print('Searching %s' % (region_name))
        images = ec2_client.describe_images(Owners=['self'])['Images']
        for image in images:
            print(image)
            for block_device_mapping in image['BlockDeviceMappings']:
                if 'Ebs' in block_device_mapping and \
                   'SnapshotId' in block_device_mapping['Ebs']:
                    snapshot_tag = "%s (%s) %s" % (
                        image['Name'],
                        image['ImageId'],
                        block_device_mapping['DeviceName'])
                    snapshot_id = block_device_mapping['Ebs']['SnapshotId']

                    print(session.resource('ec2', region_name=region_name).Snapshot(snapshot_id).create_tags(Tags=[{'Key': 'Name','Value': snapshot_tag}]))


def lambda_handler():
    create_images(response)
    time.sleep(60)
    tag_snapshots()

def main():
    lambda_handler()

if __name__ == "__main__":
    main()

