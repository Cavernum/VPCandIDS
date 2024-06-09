import logging
import time
import paramiko
import boto3
from botocore.client import ClientError
from mypy_boto3_ec2.type_defs import ReservationResponseTypeDef

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

def create_ubuntu_instance(subnet_id: str, security_groups_ids: list[str], keypair_name: str) -> ReservationResponseTypeDef:
    try:
        ec2.run_instances(
                ImageId="ami-04b70fa74e45c3917", # ubuntu
                InstanceType="t3.micro",
                KeyName=keypair_name,
                SecurityGroupIds=security_groups_ids,
                SubnetId=subnet_id,
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
            KeyName=keypair_name,
            InstanceType="t3.micro",
            SecurityGroupIds=security_groups_ids,
            SubnetId=subnet_id,
            MinCount=1,
            MaxCount=1,
            )
    return instance

def install_apache(username, private_key, public_ip_address):
    time.sleep(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(hostname=public_ip_address, username=username, pkey=private_key)

    stdin, stdout, stderr = ssh_client.exec_command("sudo apt-get update")
    stdin, stdout, stderr = ssh_client.exec_command("sudo apt-get upgrade -y")
    stdin, stdout, stderr = ssh_client.exec_command("sudo apt-get install -y apache2")

    ssh_client.close()

def install_mariadb(username, private_key, public_ip_address):
    time.sleep(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(hostname=public_ip_address, username=username, pkey=private_key)

    stdin, stdout, stderr = ssh_client.exec_command("sudo apt-get update")
    stdin, stdout, stderr = ssh_client.exec_command("sudo apt-get upgrade -y")
    stdin, stdout, stderr = ssh_client.exec_command("sudo apt-get install -y mariadb")

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
