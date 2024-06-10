import logging
import time
import boto3
import os
from botocore.client import ClientError
from mypy_boto3_ec2.type_defs import ReservationResponseTypeDef

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

def create_ubuntu_instance(name, subnet_id: str, security_groups_ids: list[str], keypair_name: str, user_data: str) -> ReservationResponseTypeDef:
    try:
        ec2.run_instances(
                ImageId="ami-04b70fa74e45c3917", # ubuntu
                InstanceType="t3.micro",
                NetworkInterfaces=[
                    {
                        "AssociatePublicIpAddress": True,
                        "DeviceIndex": 0,
                        "SubnetId": subnet_id,
                        "Groups": security_groups_ids,
                    }
                ],
                TagSpecifications=[
                    {
                        "Tags": [
                            {
                                "Key": "string",
                                "Value" : name,
                            }
                        ]
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

    instance = ec2.run_instances(
            ImageId="ami-04b70fa74e45c3917", # ubuntu
            InstanceType="t3.micro",
            NetworkInterfaces=[
                {
                    "AssociatePublicIpAddress": True,
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

    time.sleep(1)

    return instance


def download_key(instance):
    ec2=instance
    # Nom de la nouvelle paire de clés
    key_pair_name = 'key'
    # Créer une nouvelle paire de clés
    response = ec2.create_key_pair(KeyName=key_pair_name)
    # Récupérer la clé privée PEM
    key_material = response['KeyMaterial']
    # Sauvegarder la clé privée dans un fichier .pem
    with open(f'{key_pair_name}.pem', 'w') as file:
        file.write(key_material)
    # Modifier les permissions du fichier pour des raisons de sécurité
    os.chmod(f'{key_pair_name}.pem', 0o400)
    print(f"La nouvelle clé {key_pair_name}.pem a été créée.")
