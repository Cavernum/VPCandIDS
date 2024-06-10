import logging
import time
import paramiko
import boto3
import os
from botocore.client import ClientError
from mypy_boto3_ec2.type_defs import ReservationResponseTypeDef

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

def create_ubuntu_instance(subnet_id: str, security_groups_ids: list[str], keypair_name: str) -> ReservationResponseTypeDef:
    try:
        ec2.run_instances(
                ImageId="ami-04b70fa74e45c3917", # ubuntu
                InstanceType="t3.micro",
                NetworkInterfaces=[
                    {
                        "AssociatePublicIpAddress": True,
                        "DeviceIndex": 0,
                        "SubnetId": subnet_id,
                    }
                ],
                KeyName=keypair_name,
                MinCount=1,
                MaxCount=1,
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
                }
            ],
            KeyName=keypair_name,
            MinCount=1,
            MaxCount=1,
            )

    return instance

def install_dvwa(username, private_key, public_ip_address, ip_db):
    time.sleep(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(hostname=public_ip_address, username=username, pkey=private_key)

    commands = [
        "sudo apt update",
        "sudo apt install apache2 php php-mysql libapache2-mod-php git -y",
        "cd /var/www/html && sudo git clone https://github.com/digininja/DVWA.git",
        "sudo chown -R www-data:www-data /var/www/html/DVWA",
        "sudo chmod -R 755 /var/www/html/DVWA",
        "sudo cp /var/www/html/DVWA/config/config.inc.php.dist /var/www/html/DVWA/config/config.inc.php",
        f"sudo sed -i 's/db_user = ''/db_user = 'dvwa_user'/g' /var/www/html/DVWA/config/config.inc.php",
        f"sudo sed -i 's/db_password = ''/db_password = 'password_secure'/g' /var/www/html/DVWA/config/config.inc.php",
        f"sudo sed -i 's/db_database = ''/db_database = 'dvwa'/g' /var/www/html/DVWA/config/config.inc.php",
        f"sudo sed -i 's/db_server = ''/db_server = '{ip_db}'/g' /var/www/html/DVWA/config/config.inc.php",
        "sudo systemctl restart apache2"
    ]
    for command in commands:
        stdin, stdout, stderr = ssh_client.exec_command(command)

    ssh_client.close()

def install_mariadb(username, private_key, public_ip_address):
    time.sleep(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(hostname=public_ip_address, username=username, pkey=private_key)

    commands = [
        "sudo apt update",
        "sudo apt install mariadb-server -y",
        "sudo mysql -e \"CREATE DATABASE dvwa;\"",
        "sudo mysql -e \"CREATE USER 'dvwa_user'@'%' IDENTIFIED BY 'password_secure';\"",
        "sudo mysql -e \"GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa_user'@'%';\"",
        "sudo mysql -e \"FLUSH PRIVILEGES;\""
    ]
    for command in commands:
        ssh_client.exec_command(command)

    ssh_client.close()

def install_snort(username, private_key, public_ip_address):
    time.sleep(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(hostname=public_ip_address, username=username, pkey=private_key)

    stdin, stdout, stderr = ssh_client.exec_command("sudo apt update && sudo apt upgrade -y")
    stdin, stdout, stderr = ssh_client.exec_command("sudo apt install -y build-essential autotools-dev libdumbnet-dev libpcap-dev libpcre3-dev libdnet autoconf bison flex libtool")
    stdin, stdout, stderr = ssh_client.exec_command("wget https://www.snort.org/downloads/snort/daq-2.0.7.tar.gz")
    stdin, stdout, stderr = ssh_client.exec_command("tar -xzvf daq-2.0.7.tar.gz")
    stdin, stdout, stderr = ssh_client.exec_command("cd daq-2.0.7")
    stdin, stdout, stderr = ssh_client.exec_command("./configure && make && sudo make install")
    stdin, stdout, stderr = ssh_client.exec_command("cd ..")
    stdin, stdout, stderr = ssh_client.exec_command("wget https://www.snort.org/downloads/snort/snort-2.9.15.1.tar.gz")
    stdin, stdout, stderr = ssh_client.exec_command("tar -xzvf snort-2.9.15.1.tar.gz")
    stdin, stdout, stderr = ssh_client.exec_command("cd snort-2.9.15.1")
    stdin, stdout, stderr = ssh_client.exec_command("./configure --enable-sourcefire && make && sudo make install")

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

