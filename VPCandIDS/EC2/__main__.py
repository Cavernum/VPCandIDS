import logging
import boto3

# Assuming create_ubuntu_instance is defined in another part of your project
from . import create_ubuntu_instance

log = logging.getLogger(__name__)

ec2 = boto3.client("ec2")

# Subnet and security groups configuration for MariaDB instance
subnet_id = "subnet-083c46bfc1fa9cf04"
security_groups_ids = ["sg-05d36e9c88f605960"]
keypair_name = "mateo"

# Script to setup MariaDB server
script_mariadb = """#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install mariadb-server -y
sudo mysql -e "CREATE DATABASE dvwa;"
sudo mysql -e "CREATE USER 'dvwa'@'%' IDENTIFIED BY 'password_secure';"
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'dvwa'@'%';"
sudo mysql -e "FLUSH PRIVILEGES;"

sudo sed -i 's/bind-address/#&/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb.service
"""

# Create MariaDB instance without a public IP
instance_mariadb = create_ubuntu_instance(subnet_id, security_groups_ids, keypair_name, script_mariadb, public_ip=False)
instance_id_mariadb = instance_mariadb["Instances"][0]["InstanceId"]
instance_details_mariadb = ec2.describe_instances(InstanceIds=[instance_id_mariadb])["Reservations"][0]["Instances"][0]
private_ip_address_mariadb = instance_details_mariadb["PrivateIpAddress"]

# Script for DVWA setup, connecting to MariaDB instance
subnet_id = "subnet-085ce52760a32bfb7"
ip_db = private_ip_address_mariadb
script_dvwa = f"""#!/bin/bash
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

# Create DVWA instance with a public IP
security_groups_ids_dvwa = ["sg-0ceb67ec6256f2242"]
instance_dvwa = create_ubuntu_instance(subnet_id, security_groups_ids_dvwa, keypair_name, script_dvwa, public_ip=True)
instance_id_dvwa = instance_dvwa["Instances"][0]["InstanceId"]
instance_details_dvwa = ec2.describe_instances(InstanceIds=[instance_id_dvwa])["Reservations"][0]["Instances"][0]
public_ip_address_dvwa = instance_details_dvwa["PublicIpAddress"]

instance_id = instance["Instances"][0]["InstanceId"]                                              # type: ignore
instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]   # type: ignore
public_ip_address = instance["PublicIpAddress"]                                                   # type: ignore


script = """#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -qq oinkmaster snort snort-rules-default < /dev/null > /dev/null
echo "url = http://rules.emergingthreats.net/open-nogpl/snort-2.9.0/emerging.rules.tar.gz" | sudo tee -a /etc/oinkmaster.conf
sudo oinkmaster  -o /etc/snort/rules
sudo /etc/init.d/snort start
"""

security_groups_ids = ["sg-08000ebd5c259b944"]
instance = create_ubuntu_instance("Snort", subnet_id, security_groups_ids, keypair_name, script)

instance_id = instance["Instances"][0]["InstanceId"]                                              # type: ignore
instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]   # type: ignore
public_ip_address = instance["PublicIpAddress"]                                                   # type: ignore
