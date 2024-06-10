import logging
import boto3
from . import create_ubuntu_instance

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

subnet_id = "subnet-0c05177e59b75f04e"
security_groups_ids = ["sg-08000ebd5c259b944"]
keypair_name = "mateo"

# Script to setup MariaDB server
script = """#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install mariadb-server -y
sudo mysql -e "CREATE DATABASE dvwa;"
sudo mysql -e "CREATE USER 'dvwa'@'%' IDENTIFIED BY 'password_secure';"
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'dvwa'@'%';"
sudo mysql -e "FLUSH PRIVILEGES;"

sudo sed -i 's/bind-address/#&/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb.service
"""

# Create MariaDB instance
instance = create_ubuntu_instance(subnet_id, security_groups_ids, keypair_name, script)
instance_id = instance["Instances"][0]["InstanceId"]
instance_details = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
private_ip_address_mariadb = instance_details["PrivateIpAddress"]

# Further configuration for DVWA setup
ip_db = private_ip_address_mariadb
script = f"""#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install apache2 mariadb-client php php-mysqli php-gd libapache2-mod-php git -y
cd /var/www/html && sudo git clone https://github.com/digininja/DVWA.git
sudo chown -R www-data:www-data /var/www/html/DVWA
sudo chmod -R 755 /var/www/html/DVWA
sudo cp /var/www/html/DVWA/config/config.inc.php.dist /var/www/html/DVWA/config/config.inc.php
sudo sed -i 's/127.0.0.1/{ip_db}/g' /var/www/html/DVWA/config/config.inc.php
sudo sed -i 's/p@ssw0rd/password_secure/g' /var/www/html/DVWA/config/config.inc.php
sudo sed -i 's/impossible/low/g' /var/www/html/DVWA/config/config.inc.php
sudo systemctl restart apache2
"""

# Subnet and security groups configuration for DVWA instance
security_groups_ids = ["sg-0ceb67ec6256f2242"]
instance = create_ubuntu_instance("DVWA", subnet_id, security_groups_ids, keypair_name, script, public_ip=True)
instance_id = instance["Instances"][0]["InstanceId"]
instance_details = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
private_ip_address_dvwa = instance_details["PrivateIpAddress"]

script = """
sudo apt update && sudo apt upgrade -y

"""

security_groups_ids = ["sg-08000ebd5c259b944"]
instance = create_ubuntu_instance("Snort", subnet_id, security_groups_ids, keypair_name, script)

instance_id = instance["Instances"][0]["InstanceId"]                                              # type: ignore
instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]   # type: ignore
public_ip_address = instance["PublicIpAddress"]                                                   # type: ignore
