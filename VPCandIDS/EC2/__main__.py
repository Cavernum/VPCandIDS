import logging
import boto3
import paramiko

from . import create_ubuntu_instance, install_dvwa, install_mariadb

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

subnet_id = "subnet-0a128191bd2bebb4d"
security_groups_ids = ["sg-08cd754b67995f08e"]
keypair_name = "mateo"
instance = create_ubuntu_instance(subnet_id, security_groups_ids, keypair_name)

instance_id = instance["Instances"][0]["InstanceId"]                                              # type: ignore
instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]   # type: ignore
public_ip_address = instance["PublicIpAddress"]                                                   # type: ignore

ssh_username = "ubuntu"
ssh_key_file = "mateo.pem"
private_key = paramiko.RSAKey.from_private_key_file(ssh_key_file)

install_mariadb(ssh_username, private_key, public_ip_address)



ip_db = public_ip_address

security_groups_ids = ["sg-0a7bf2819224ad4db"]
instance = create_ubuntu_instance(subnet_id, security_groups_ids, keypair_name)

instance_id = instance["Instances"][0]["InstanceId"]                                              # type: ignore
instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]   # type: ignore
public_ip_address = instance["PublicIpAddress"]                                                   # type: ignore

install_dvwa(ssh_username, private_key, public_ip_address, ip_db)
