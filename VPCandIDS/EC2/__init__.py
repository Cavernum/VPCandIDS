import logging
import time
import boto3
import os
from botocore.client import ClientError

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

def create_ubuntu_instance(subnet_id: str, security_groups_ids: list[str], keypair_name: str, user_data: str, public_ip=False):
    try:
        # Dry run to check permissions
        ec2.run_instances(
            ImageId="ami-04b70fa74e45c3917",  # Replace with the AMI ID for Ubuntu or your preferred AMI
            InstanceType="t3.micro",
            NetworkInterfaces=[
                {
                    "AssociatePublicIpAddress": public_ip,  # Instance will not have a public IP
                    "DeviceIndex": 0,
                    "SubnetId": subnet_id,
                    "Groups": security_groups_ids,
                }
            ],
            KeyName=keypair_name,
            MinCount=1,
            MaxCount=1,
            UserData=user_data,
            DryRun=True
        )
    except ClientError as e:
        if "DryRun" not in str(e):
            raise
        log.info("EC2 instance creation DryRun succeeded.")

    # Actual instance creation
    instance = ec2.run_instances(
        ImageId="ami-04b70fa74e45c3917",  # Again, replace with your preferred AMI
        InstanceType="t3.micro",
        NetworkInterfaces=[
            {
                "AssociatePublicIpAddress": public_ip,  # Ensure this is set to False
                "DeviceIndex": 0,
                "SubnetId": subnet_id,
                "Groups": security_groups_ids,
            }
        ],
        KeyName=keypair_name,
        MinCount=1,
        MaxCount=1,
        UserData=user_data,
    )

    time.sleep(1)  # Waiting a bit after instance creation

    return instance

def download_key(instance):
    ec2 = instance
    key_pair_name = 'key'
    response = ec2.create_key_pair(KeyName=key_pair_name)
    key_material = response['KeyMaterial']

    with open(f'{key_pair_name}.pem', 'w') as file:
        file.write(key_material)

    os.chmod(f'{key_pair_name}.pem', 0o400)
    print(f"La nouvelle clé {key_pair_name}.pem a été créée.")
