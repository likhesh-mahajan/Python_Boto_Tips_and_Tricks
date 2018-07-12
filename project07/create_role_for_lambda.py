import boto3
client = boto3.client('iam')

response_create_role = \
client.create_role(RoleName='ServerlessAdminTest',AssumeRolePolicyDocument='{  \
"Version": "2012-10-17", "Statement": [ { "Sid": "", "Effect": "Allow", \
"Principal": { "Service": "lambda.amazonaws.com" }, "Action": "sts:AssumeRole" } ]}')

print(response_create_role)

response = client.attach_role_policy(RoleName='ServerlessAdminTest', PolicyArn='arn:aws:iam::aws:policy/PowerUserAccess')

print(response)

