import logging
import boto3
import paramiko

from . import create_ubuntu_instance, install_apache, install_mariadb

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

subnet_id = "subnet-05d3fb30d62d29f1b"
security_groups_ids = [""]
keypair_name = ""
instance = create_ubuntu_instance(subnet_id, security_groups_ids, keypair_name)

instance_id = instance["Instances"][0]["InstanceId"]                                              # type: ignore
instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]   # type: ignore
public_ip_address = instance["PublicIpAddress"]                                                   # type: ignore

ssh_username = "ubuntu"
ssh_key_file = "mateo.pem"
private_key = paramiko.RSAKey.from_private_key_file(ssh_key_file)

install_apache(ssh_username, private_key, public_ip_address)
install_mariadb(ssh_username, private_key, public_ip_address)
