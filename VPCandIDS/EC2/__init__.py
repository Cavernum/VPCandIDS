import logging
import time
import boto3
import os
from botocore.client import ClientError

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

<<<<<<< HEAD
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
=======
def create_ubuntu_instance(subnet_id: str, security_groups_ids: list[str], keypair_name: str, user_data: str, *, public_ip=False):
    try:
        ec2.run_instances(
            ImageId="ami-04b70fa74e45c3917", 
>>>>>>> 7abc558 (No public IP for db server)
            InstanceType="t3.micro",
            NetworkInterfaces=[
                {
                    "AssociatePublicIpAddress": public_ip,  
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

    instance = ec2.run_instances(
        ImageId="ami-04b70fa74e45c3917",  
        InstanceType="t3.micro",
        NetworkInterfaces=[
            {
                "AssociatePublicIpAddress": public_ip,
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

<<<<<<< HEAD

def download_key(file_name,path):
    path = os.path.realpath(path)
    ec2 = boto3.client("ec2")
    # Nom de la nouvelle paire de clés
    key_pair_name = file_name
        # Vérifier si la paire de clés existe déjà
    try:
        existing_key_pairs = ec2.describe_key_pairs(KeyNames=[key_pair_name])
        if existing_key_pairs['KeyPairs']:
            log.warn("La paire de clés existe déjà. Elle va être supprimée.")
            # Supprimer la paire de clés existante
            ec2.delete_key_pair(KeyName=key_pair_name)
            log.info(f"La paire de clés existante '{key_pair_name}' a été supprimée.")
    except ec2.exceptions.ClientError as e:
        if 'InvalidKeyPair.NotFound' in str(e):
            log.info(f"Aucune paire de clés existante trouvée avec le nom '{key_pair_name}'.")
        else:
            log.info(f"Erreur lors de la vérification de la paire de clés: {e}")
            return
    # Créer une nouvelle paire de clés
=======
def download_key(instance):
    ec2 = instance
    key_pair_name = 'key'
>>>>>>> 7abc558 (No public IP for db server)
    response = ec2.create_key_pair(KeyName=key_pair_name)
    key_material = response['KeyMaterial']
<<<<<<< HEAD
    # Sauvegarder la clé privée dans un fichier .pem
    with open(os.path.join(path, f"{key_pair_name}.pem"), 'w') as file:
        file.write(key_material)
    # Modifier les permissions du fichier pour des raisons de sécurité
    os.chmod(f'{path}/{key_pair_name}.pem', 0o400)
    log.info(f"La nouvelle clé {key_pair_name}.pem a été créée.")

def search_key(file_name):
    path = os.path.realpath('./KEYS')
    contents = os.listdir(path)
    for e in contents:
        if e==f"{file_name}.pem":
            log.info(f"La paire de clé {file_name} a été trouvée.")
            return e
    log.warn(f"La paire de clé {file_name} n'a pas été trouvée.")

    
=======

    with open(f'{key_pair_name}.pem', 'w') as file:
        file.write(key_material)

    os.chmod(f'{key_pair_name}.pem', 0o400)
    print(f"La nouvelle clé {key_pair_name}.pem a été créée.")
>>>>>>> 7abc558 (No public IP for db server)
