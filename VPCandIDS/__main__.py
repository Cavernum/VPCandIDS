#!/usr/bin/env python3
banner = """
 _____________
< VPC and IDS >
 -------------
        \\   ^__^
         \\  (xx)\\_______
            (__)\\       )\\/\\
             U  ||----w |
                ||     ||
"""

__author__ = "Lachaize Matéo, Iglesias Guillaume, Dufour Nils"
__credits__ = [ "Lachaize Matéo", "Iglesias Guillaume", "Dufour Nils" ]
__version__ = "1.0.0"
__email__ = "dufour.e2101101@etud.univ-ubs.fr"

import argparse
import builtins
import logging

import boto3
from rich.console import Console
from rich.progress import track
from rich.status import Status

from . import EC2, logger
from .vpc import subnets, gateways, routes, acls, security_groups

log = logging.getLogger(__name__)
stdout = Console(tab_size=2)
builtins.print = stdout.print
ec2 = boto3.client('ec2')


print(f"[red]{ banner }[/red]")

parser = argparse.ArgumentParser(
        description="Deploy VPC, subnets, gateways, 3 instances and trafic mirroring.",
        epilog=f"Written by {__author__}",
        )
parser.add_argument("-l", "--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR", "FATAL"], default="WARN")
args = parser.parse_args()

logger.enable(log_level=args.log_level)


class OurStatus(Status):
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        print(f"✅ { self.status }")
        return


################################################################################
#                 _   _      _                      _                          #
#                | \ | | ___| |___      _____  _ __| | __                      #
#                |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /                      #
#                | |\  |  __/ |_ \ V  V / (_) | |  |   <                       #
#                |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\                      #
#                                                                              #
################################################################################

with OurStatus("Creating VPC"):
    new_vpc = subnets.create_custom_vpc('10.0.0.0/16','Name', 'myVPC')
    log.info("Created VPC.")
    log.debug(new_vpc)
    vpc_id = new_vpc["Vpc"]["VpcId"]                              # type: ignore


with OurStatus("Creating subnets"):
    public_subnet = subnets.create_subnet_perso(
        "us-east-1a",
        "10.0.0.0/24",
        vpc_id,
        "Name", "Pub-Sub"
    )
    log.info("Created public subnet.")
    log.debug(public_subnet)
    public_subnet_id = public_subnet["Subnet"]["SubnetId"]        # type: ignore

    private_subnet = subnets.create_subnet_perso(
        "us-east-1a",
        "10.0.1.0/24",
        vpc_id,
        "Name", "Priv-Sub"
    )
    log.info("Created private subnet.")
    log.debug(private_subnet)
    private_subnet_id = private_subnet["Subnet"]["SubnetId"]      # type: ignore


with OurStatus("Creating gateways"):
    internet_gateway = gateways.create_internet_gateway(
        vpc_id,
        "Name",
        "Internet-GW"
    )
    log.info("Created internet gateway.")
    log.debug(internet_gateway)

    nat_gateway = gateways.create_nat_gateway(
        public_subnet_id,
        "Name", "EIP",
        "Name", "Nat-GW"
    )
    nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']    # type: ignore
    log.info("Created NAT gateway.")
    log.debug(nat_gateway)


with OurStatus("Waiting for NAT Gateway to attach"):
    waiter = ec2.get_waiter('nat_gateway_available')

    waiter.wait(
        NatGatewayIds=[nat_gateway_id],
        WaiterConfig={
            "Delay": 5,
            "MaxAttempts": 30
        }
    )
    log.info("NAT gateway is now attached, continuing...")
    log.debug(f"NAT Gateway ID: {nat_gateway_id}")


with OurStatus("Creating routes"):
    public_route = routes.create_public_route(
        vpc_id,
        "0.0.0.0/0",
        internet_gateway["InternetGateway"]["InternetGatewayId"], # type: ignore
        "Name", "Public-Route"
    )
    log.info("Created route 0.0.0.0/0 to Internet Gateway.")
    log.debug(public_route)

    private_route = routes.create_private_route(
        vpc_id,
        "0.0.0.0/0",
        nat_gateway_id,
        "Name", "Private-Route"
    )
    log.info("Created route 0.0.0.0/0 for private subnet.")
    log.debug(private_route)


with OurStatus("Associating routing tables to subnets"):
    private_route_to_subnet = routes.association_tableRoutage_subnet(
        private_route["RouteTable"]["RouteTableId"],              # type: ignore
        private_subnet_id
    )
    log.info("Created association between private route and private subnet.")
    log.debug(private_route_to_subnet)

    public_route_subnet = routes.association_tableRoutage_subnet(
        public_route["RouteTable"]["RouteTableId"],               # type: ignore
        public_subnet_id
    )
    log.info("Created association between public route and public subnet.")
    log.debug(public_route_subnet)


with OurStatus("Creating NACLs"):
    nacls = acls.create_and_configure_nacl(
        vpc_id,
        public_subnet_id,
        private_subnet_id
    )
    log.info("Created NACLs.")
    log.debug(nacls)


with OurStatus("Creating security groups"):
    web_sg_id, db_sg_id = security_groups.create_security_groups(vpc_id)

################################################################################
#                             _____ ____ ____                                  #
#                            | ____/ ___|___ \                                 #
#                            |  _|| |     __) |                                #
#                            | |__| |___ / __/                                 #
#                            |_____\____|_____|                                #
#                                                                              #
################################################################################

with OurStatus("Creating MariaDB instance"):
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
    log.debug(script_mariadb)

    EC2.download_key("mariadb")
    mariadb = EC2.create_ubuntu_instance(
        "MariaDB",
        private_subnet_id,
        [db_sg_id],
        "mariadb",
        script_mariadb
    )
    mariadb_priv_ip = mariadb["Instances"][0]["PrivateIpAddress"] # type: ignore
    log.info("Created MariaDB instance.")
    log.debug(mariadb)


with OurStatus("Creating DVWA instance"):
    script_dvwa = f"""#!/bin/bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install apache2 mariadb-client php php-mysqli php-gd libapache2-mod-php git -y
    cd /var/www/html && sudo git clone https://github.com/digininja/DVWA.git
    sudo chown -R www-data:www-data /var/www/html/DVWA
    sudo chmod -R 755 /var/www/html/DVWA
    sudo cp /var/www/html/DVWA/config/config.inc.php.dist /var/www/html/DVWA/config/config.inc.php
    sudo sed -i 's/127.0.0.1/{mariadb_priv_ip}/g' /var/www/html/DVWA/config/config.inc.php
    sudo sed -i 's/p@ssw0rd/password_secure/g' /var/www/html/DVWA/config/config.inc.php
    sudo sed -i 's/impossible/low/g' /var/www/html/DVWA/config/config.inc.php
    sudo systemctl restart apache2
    """
    log.debug(script_dvwa)

    EC2.download_key("dvwa")
    dvwa = EC2.create_ubuntu_instance(
        "DVWA",
        public_subnet_id,
        [web_sg_id],
        "dvwa",
        script_dvwa,
        public_ip=True,
    )
    log.info("Created DVWA instance.")
    log.debug(dvwa)


with OurStatus("Creating Snort instance"):
    script_snort =  """#!/bin/bash
    sudo apt update && sudo apt upgrade -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -qq oinkmaster snort snort-rules-default < /dev/null > /dev/null
    echo "url = http://rules.emergingthreats.net/open-nogpl/snort-2.9.0/emerging.rules.tar.gz" | sudo tee -a /etc/oinkmaster.conf
    sudo oinkmaster  -o /etc/snort/rules

    echo 'include $RULE_PATH/community-sql-injection.rules' | sudo tee -a /etc/snort/snort.conf
    echo 'include $RULE_PATH/emerging-sql.rules' | sudo tee -a /etc/snort/snort.conf
    echo 'include $RULE_PATH/mysql.rules' | sudo tee -a /etc/snort/snort.conf
    """
    log.debug(script_snort)

    EC2.download_key("snort")
    snort = EC2.create_ubuntu_instance(
        "Snort",
        private_subnet_id,
        [db_sg_id],
        "snort",
        script_snort
    )


################################################################################
#                      __  __ _                                                #
#                     |  \/  (_)_ __ _ __ ___  _ __                            #
#                     | |\/| | | '__| '__/ _ \| '__|                           #
#                     | |  | | | |  | | | (_) | |                              #
#                     |_|  |_|_|_|  |_|  \___/|_|                              #
#                                                                              #
################################################################################

# Now follow the presentation :)
