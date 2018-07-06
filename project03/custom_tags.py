from datetime import datetime
import boto3


ec2 = boto3.resource('ec2', region_name="us-east-1")

mydate = ((str(datetime.now())).split(' ')[0]).split('-')[2] + '-' + ((str(datetime.now())).split(' ')[0]).split('-')[1] + '-' + ((str(datetime.now())).split(' ')[0]).split('-')[0]

custom = "i-0c0ce83a2cfacf8d4"


mytags = [{
    "Key" : "DateChecked",
       "Value" : repr(mydate)
    },
    {
       "Key" : "Name",
       "Value" : "i-0f8bcca1e282d4649"
    },
    {
       "Key" : "Environment",
       "Value" : "Production"
    }]

othertags = [{
    "Key" : "DateChecked",
       "Value" : repr(mydate)
    },
    {
       "Key" : "VolId",
       "Value" : "vol-0c0ce83a2cfacf8d4"
    },
    {
       "Key" : "Environment",
       "Value" : "Development"
    }]


def lambda_handler(event, context):
    servers = ec2.instances.all()
    temptags = []
    customtags = []
    tagvalue = {}
    sometags = {}
    for instance in servers:
        if instance.id == custom:
            sometags['Key'] = 'Name'
            sometags['Value'] = custom
            customtags.append(sometags)
            instance.create_tags(instance.tags,Tags=customtags)
            continue
        if not instance.tags:
            tagvalue['Value'] = " Email devops@buildmystartup.io to customize this tag"
            tagvalue['Key'] = 'Name'
            temptags.append(tagvalue)
            instance.create_tags(instance.tags,Tags=temptags)
            continue
        for myinstance in instance.tags:
            instance.create_tags(myinstance,Tags=othertags)


def main():
    lambda_handler(None, None)

if __name__ == "__main__":
    main()
