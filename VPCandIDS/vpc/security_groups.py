import boto3

def create_security_groups(vpc_id):
    ec2 = boto3.resource('ec2')

    sg_web = ec2.create_security_group(
        GroupName='WebServerSG',
        Description='Security group for web server',
        VpcId=vpc_id
    )
    sg_web.authorize_egress(
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 1,
                'ToPort': 65000,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
        ]
    )
    sg_web.authorize_ingress(
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 1,
                'ToPort': 65000,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            # {
            #     'IpProtocol': 'tcp',
            #     'FromPort': 80,
            #     'ToPort': 80,
            #     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            # },
            # {
            #     'IpProtocol': 'tcp',
            #     'FromPort': 443,
            #     'ToPort': 443,
            #     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            # }
        ]
    )

    sg_db = ec2.create_security_group(
        GroupName='DatabaseServerSG',
        Description='Security group for database server',
        VpcId=vpc_id
    )
    sg_db.authorize_egress(
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 1,
                'ToPort': 65000,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
        ]
    )
    sg_db.authorize_ingress(
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 1,
                'ToPort': 65000,
                'UserIdGroupPairs': [{'GroupId': sg_web.group_id}]
            },
            # {
            #     'IpProtocol': 'tcp',
            #     'FromPort': 3306,
            #     'ToPort': 3306,
            #     'UserIdGroupPairs': [{'GroupId': sg_web.group_id}]
            # }
        ]
    )

    return sg_web.group_id, sg_db.group_id

