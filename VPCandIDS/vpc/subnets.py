import boto3
ec2 = boto3.client('ec2')

def create_custom_vpc(cidr_block, tags_key, tags_value):
    vpcmain = ec2.create_vpc(
        CidrBlock=cidr_block,
        TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags': [
                    {
                        'Key': tags_key,
                        'Value': tags_value
                    },
                ]
            },
        ]
    )
    return vpcmain


def create_subnet_perso(az, cidr_block, vpc_id, tags_key, tags_value):
    subnet = ec2.create_subnet(
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': tags_key,
                        'Value': tags_value
                    },
                ]
            },
        ],
        AvailabilityZone=az,
        CidrBlock=cidr_block,
        VpcId=vpc_id,
    )
    return subnet