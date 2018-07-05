import boto3

iam = boto3.client('iam')

for myusers in iam.list_users()['Users']:
    myGroups = iam.list_groups_for_user(UserName=myusers['UserName'])
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Username: "  + myusers['UserName'])
    print("Assigned groups: ")
    for yourgroupName in myGroups['Groups']:
        print(yourgroupName['GroupName'])
