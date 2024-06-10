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
#   _   _      _                      _                                        #
#  | \ | | ___| |___      _____  _ __| | __                                    #
#  |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /                                    #
#  | |\  |  __/ |_ \ V  V / (_) | |  |   <                                     #
#  |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\                                    #
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
    log.info("Created NAT gateway.")
    log.debug(nat_gateway)


with OurStatus("Creating routes"):
    public_route= routes.create_public_route(
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
        "Name", "Private-Route"
    )
    log.info("Created route 0.0.0.0/0 for private subnet.")
    log.debug(private_route)


with OurStatus("Waiting for NAT Gateway to attach"):
    nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']    # type: ignore
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
#  _____ ____ ____                                                             #
# | ____/ ___|___ \                                                            #
# |  _|| |     __) |                                                           #
# | |__| |___ / __/                                                            #
# |_____\____|_____|                                                           #
#                                                                              #
################################################################################


