import logging
import time
import boto3
import os

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

def create_ubuntu_instance(name: str, subnet_id: str, security_groups_ids: list[str], keypair_name: str, user_data: str, *, public_ip=False):
    instance = ec2.run_instances(
            ImageId="ami-04b70fa74e45c3917", # ubuntu
            InstanceType="t3.micro",
            NetworkInterfaces=[
                {
                    "AssociatePublicIpAddress": public_ip,  # Instance will not have a public IP
                    "DeviceIndex": 0,
                    "SubnetId": subnet_id,
                    "Groups": security_groups_ids,
                }
            ],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {
                            "Key": "Name",
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
    time.sleep(1)  # Waiting a bit after instance creation

    return instance

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
    response = ec2.create_key_pair(KeyName=key_pair_name)
    # Récupérer la clé privée PEM
    key_material = response['KeyMaterial']
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
